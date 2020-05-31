import csv
import os
import subprocess
import time


PRODUCTION = os.getenv("PRODUCTION")

LABEL_FILE = os.path.join(os.path.dirname(__file__), "glabels", "label.glabels")

TMP_DIR = os.path.join(os.path.dirname(__file__), "tmp")
LABEL_CSV = os.path.join(TMP_DIR, "label_data.csv")
PRINT_PDF = os.path.join(TMP_DIR, "labels.pdf")
MERGE_CSV = os.path.join(TMP_DIR, "merge.csv")


class LabelFileError(Exception):
    pass


class LabelSet(object):
    def __init__(self, customer, cultivar, lot, trays):
        self.Customer = customer
        self.Cultivar = cultivar
        self.Lot = lot
        self.Trays = trays
        self.Printed = 0


class CultivarData(object):
    def __init__(self, cultivar, sow_date):
        self.SowDate = sow_date
        self.Cultivar = cultivar
        self.LotNumber = None
        self.TrayCount = None
        self.Printed = 0
        self.LabelSets = []


def printLabel(label_set_groups):
    '''
    Prints one label per given label set
    (label_set, tray_number)
    '''
    # Generate the temporary csv file to merge with the labels
    contents = [["Customer", "Cultivar", "Tray", "Lot"]]
    for label_set, tray in label_set_groups:
        contents.append([label_set.Customer, label_set.Cultivar, tray, label_set.Lot])
    
    with open(MERGE_CSV, "w") as f:
        w = csv.writer(f)
        for row in contents:
            w.writerow(row)
    
    # generate the pdf to print
    if PRODUCTION:
        subprocess.run(["glabels-3-batch", "-i", MERGE_CSV, "-o", PRINT_PDF, LABEL_FILE])
        subprocess.run(["lp", PRINT_PDF])
    else:
        time.sleep(1.5)

    # glabels-3-batch -i <input.csv> -o <output.pdf> <label.glabel>
    # lp <output.pdf>
    return


def saveLabelDataFile(csv_file):
    csv_file.save(LABEL_CSV)
    getFileContents()


def getFileContents():
    if not os.path.isfile(LABEL_CSV):
        raise LabelFileError("No file uploaded")

    try:
        contents = []
        with open(LABEL_CSV) as f:
            reader = csv.reader(f)
            for row in reader:
                contents.append(row)
    except:
        raise LabelFileError("Not a CSV File")

    # Validate the data
    if not "Sow Date" in contents[0][0]:
        raise LabelFileError("Bad file. Sow Date not found")
    if not "Lots" in contents[1][2]:
        raise LabelFileError("Bad file. Lot information not found")

    if not "Customer" in contents[4][0]:
        raise LabelFileError("Bad file. Customer information not found")

    return contents
    

def parseFile():
    contents = getFileContents()   
    #
    # Organize the data
    #
    sow_date = contents[0][1]


    # Get each unique cultivar name
    cultivars = []
    for idx in range(len(contents[3])):
        c = contents[3][idx]
        if c == "" and not cultivars:
            continue
        elif c == "" and cultivars:
            cultivar_start_idx = idx+2
            break
        else:
            cultivars.append(CultivarData(c, sow_date))

    # attach the lot numbers
    idx = 3
    for c in cultivars:
        c.LotNumber = contents[1][idx]
        idx += 1

    # get cultivar positions in the customer table
    cultivar_idxs = {}
    idx = cultivar_start_idx
    for c in cultivars:
        cultivar_idxs[idx] = c.Cultivar
        idx += 2

    # Cultivar map
    cultivar_map = {}
    for c in cultivars:
        cultivar_map[c.Cultivar] = c

    # Build Customer label sets
    for row in contents[5:]:
        customer = row[0]
        for idx,c in cultivar_idxs.items():
            if row[idx] not in ["0", ""]:
                trays = int(row[idx])
                cultivar = cultivar_map[c]
                cultivar.LabelSets.append(LabelSet(customer, c, cultivar.LotNumber, trays))
    
    # Sum the tray counts
    for c in cultivars:
        c.TrayCount = sum([ls.Trays for ls in c.LabelSets])
    
    return cultivars


    


