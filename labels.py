import csv
import os
import subprocess
import time


PRODUCTION = os.getenv("PRODUCTION")
DEFAULT_LABEL_TYPE = "commercial"

LABEL_DIR = os.path.join(os.path.dirname(__file__), "glabels")

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
        self.Seeds = 0

    def __repr__(self):
        return "%s: %s - %s, %s"%(self.Customer, self.Cultivar, self.Lot, self.Trays)


class CultivarData(object):
    def __init__(self, cultivar, sow_date):
        self.SowDate = sow_date
        self.Cultivar = cultivar

        self.LotNumber = None
        self.TrayCount = None
        self.Printed = 0
        self.LabelSets = []


def _print(label_type):
    # generate the pdf to print
    if PRODUCTION:
        label_file = os.path.join(LABEL_DIR, label_type+".glabels")
        subprocess.run(["glabels-3-batch", "-i", MERGE_CSV, "-o", PRINT_PDF, label_file])
        subprocess.run(["lp", PRINT_PDF])
    else:
        print("Printed!")
        time.sleep(1.5)

    # glabels-3-batch -i <input.csv> -o <output.pdf> <label.glabel>
    # lp <output.pdf>


def printLabel(label_set_groups, label_type=None):
    '''
    Prints one label per given label set
    [(label_set, tray_number)], label_type
    '''
    if label_type is None:
        label_type = DEFAULT_LABEL_TYPE
    
    # Generate the temporary csv file to merge with the labels
    contents = [["Customer", "Cultivar", "Tray", "Lot"]]
    label_type = DEFAULT_LABEL_TYPE
    for label_set, tray in label_set_groups:
        contents.append([label_set.Customer, label_set.Cultivar, tray, label_set.Lot])
    
    with open(MERGE_CSV, "w") as f:
        w = csv.writer(f)
        for row in contents:
            w.writerow(row)
    
    _print(label_type)
    return


def printCSV(csv_file, label_type):
    csv_file.save(MERGE_CSV)
    rows = []
    with open(MERGE_CSV) as f:
        reader = csv.reader(f)
        rows = [row for row in reader]

    if len(rows) < 2:
        raise LabelFileError("Not enough rows")

    if "Customer" not in rows[0]:
        raise LabelFileError("No Customer in header")
    if "Cultivar" not in rows[0]:
        raise LabelFileError("No Cultivar in header")
    if "Tray" not in rows[0]:
        raise LabelFileError("No Tray in header")
    if "Lot" not in rows[0]:
        raise LabelFileError("No Lot in header")

    _print(label_type)


def saveLabelDataFile(csv_file, label_type):
    global DEFAULT_LABEL_TYPE
    DEFAULT_LABEL_TYPE = label_type
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
    # if not "Sow Date" in contents[0][0]:
    #     raise LabelFileError("Bad file. Sow Date not found")
    # if not "Lots" in contents[1][2]:
    #     raise LabelFileError("Bad file. Lot information not found")

    # if not "Customer" in contents[4][0]:
    #     raise LabelFileError("Bad file. Customer information not found")

    return contents
    


# def parseFile():
#     contents = getFileContents()   
#     #
#     # Organize the data
#     #
#     sow_date = contents[0][1]


#     # Get each unique cultivar name
#     cultivars = []
#     for idx in range(len(contents[3])):
#         c = contents[3][idx]
#         if c == "" and not cultivars:
#             continue
#         elif c == "" and cultivars:
#             cultivar_start_idx = idx+2
#             break
#         else:
#             cultivars.append(CultivarData(c, sow_date))

#     # attach the lot numbers
#     idx = 3
#     for c in cultivars:
#         c.LotNumber = contents[1][idx]
#         idx += 1

#     # get cultivar positions in the customer table
#     cultivar_idxs = {}
#     idx = cultivar_start_idx
#     for c in cultivars:
#         cultivar_idxs[idx] = c.Cultivar
#         idx += 2

#     # Cultivar map
#     cultivar_map = {}
#     for c in cultivars:
#         cultivar_map[c.Cultivar] = c

#     # Build Customer label sets
#     for row in contents[5:]:
#         customer = row[0]
#         for idx,c in cultivar_idxs.items():
#             if row[idx] not in ["0", ""]:
#                 trays = int(row[idx])
#                 cultivar = cultivar_map[c]
#                 cultivar.LabelSets.append(LabelSet(customer, c, cultivar.LotNumber, trays))
    
#     # Sum the tray counts
#     for c in cultivars:
#         c.TrayCount = sum([ls.Trays for ls in c.LabelSets])
    
#     return cultivars

def parseFile():
    """
    Reads the temporary file and returns a list of CultivarData objects
    """
    contents = getFileContents()   
    #
    # Collect header data
    #
    sow_date = contents[0][1]
    # base_lot = contents[1][1]
    customer = contents[2][1]
    
    #
    # Cultivars start on row 6, which is row 5 with 0 indexing
    # The table is: Cultivar Name, Lot Number, Seeds, Trays
    header_row = 5-1
    cultivar_row = 6-1

    # Rows:
    name_idx = 0
    lot_idx = 1
    seed_idx = 2
    tray_idx = 3
    sown_idx = 4

    # Confirm header and columns
    # raise LabelFileError("")

    # Process the cultivar table
    cultivars = []
    for row in contents[cultivar_row:]:
        name = row[name_idx]
        if name == "":
            break
        else:
            lot_number = row[lot_idx]
            trays = int(row[tray_idx])

            cd = CultivarData(name, sow_date)
            ls = LabelSet(customer, name, lot_number, trays)
            ls.Seeds = row[seed_idx]

            cd.LabelSets.append(ls)
            cd.TrayCount = ls.Trays

            if len(row) > sown_idx:
                ls.Printed = int(row[sown_idx])
                cd.Printed = ls.Printed

            cultivars.append(cd)

    return cultivars


def saveFile(cultivars):
    """
    Write the progress back to the file
    """
    contents = getFileContents()
    #
    # Cultivars start on row 6, which is row 5 with 0 indexing
    # The table is: Cultivar Name, Lot Number, Seeds, Trays
    header_row = 5-1
    cultivar_row = 6-1

    # Rows:
    name_idx = 0
    lot_idx = 1
    seed_idx = 2
    tray_idx = 3
    sown_idx = 4

    with open(LABEL_CSV, "w") as f:
        csv_writer = csv.writer(f)
        # Write the pre-amble
        for x in range(header_row):
            csv_writer.writerow(contents[x])

        # write the header row
        if len(contents[x+1]) < sown_idx:
            csv_writer.writerow(contents[x+1]+["Sown"])
        else:
            csv_writer.writerow(contents[x+1])

        # Write the new culitvar rows
        for cultivar_data in cultivars:
            for label_set in cultivar_data.LabelSets:
                row = [label_set.Cultivar, label_set.Lot, label_set.Seeds, label_set.Trays, label_set.Printed]
                csv_writer.writerow(row)
