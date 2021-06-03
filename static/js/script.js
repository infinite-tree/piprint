function show_error_message(error_message){
    var error_msg_div = $('#error-message-box p');
    error_msg_div.text(error_message);
    error_div.show();
    console.log("Error");
    console.log(error_message);
}



function submitForm (number) {
    event.stopPropagation();
    event.preventDefault();

    $('#errors').html('');

    console.log("Action: "+ number);
    var url = "/upload-file";
    if (number == 2) {
        url = "/print-file";
    }

    if (typeof files != 'undefined') {
        uploadFiles(url);
    } else {
        show_error_message('Please upload a file to proceed.');
    }
}

function prepareUpload(event){
    files = event.target.files;
}

function uploadFiles(url){
    var data = new FormData(),
        submit_button = $('#submit_button'),
        page_form = submit_button.parent('form'),
        file_input = page_form.children('input[name="file"]');

    $.each(files, function(key, value){
        data.append(key, value);
    });

    data.set("label_type", label_type);

    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        cache: false,
        dataType: 'json',
        processData: false,
        contentType: false,

        success: function(response){
            upload_prompt_div.hide();
            back_nav.show();
            if(response.success){
                upload_results_div.show();
                results_div.append('<b>Success</b>');
            } else {
                show_error_message(response.error_message);
            }
        },
        error: function(jqXHR, textStatus, errorThrown){
            upload_prompt_div.hide();
            back_nav.show();
            error_message = 'Some technical glitch! Please retry after reloading the page!';
            show_error_message(error_message);
        },
        beforeSend: function(){
            submit_button.val('Uploading...');
            submit_button.attr('disabled', '');

            file_input.attr('disabled', '');
        },
        complete: function(){
            submit_button.val('Upload');
            submit_button.removeAttr('disabled');

            file_input.removeAttr('disabled');
            $('#results').minEmoji();
        }
    });
}


function restoreForm(event) {
    event.preventDefault();

    results_div.empty();
    back_nav.hide();
    upload_prompt_div.show();
    error_div.hide();
    upload_results_div.hide();
}


var labelForm;
function labelFormSetup() {
	//Setup the single label form
	labelForm = document.forms['single-label-form'];
	labelForm.addEventListener('submit', e => {
		e.preventDefault();
        
        var data = new FormData(labelForm);
        data.set("label_type", label_type);
		fetch("/print-single-label", {
            method: 'POST',
            body: data
        }).then(response => response.json()).then(data => {

            upload_prompt_div.hide();
            back_nav.show();
            if(data.success){
                $('#label_form').trigger('reset');
                upload_results_div.show();
                results_div.append('<b>Success</b>');
            } else {
                show_error_message(data.error_message);
            }
        }).catch(error => {
            upload_prompt_div.hide();
            back_nav.show();
            show_error_message(error);
        });
	});
}

function buttonGroupSetup() {
  $('#labelTypeGroup button').on('click', function() {
    var thisBtn = $(this);
    
    thisBtn.addClass('active').siblings().removeClass('active');
    var btnText = thisBtn.text();
    var btnValue = thisBtn.val();
    console.log(btnText + ' - ' + btnValue);    
    $('#selectedVal').text(btnValue);

    label_type = btnValue;

    // set the image to show
    $('#img-commercial').hide();
    $('#img-retail').hide();
    $('#img-seed').hide();
    $('#img-'+btnValue).show();

  });
  
  // Set default value
  $('#labelTypeGroup button[value="commercial"]').click();
}


$(document).ready(function(){
    $('input[type=file]').on('change', prepareUpload);
    $('.nav-back').click(restoreForm);
    $('#error-button').click(restoreForm);
    $('#done-button').click(restoreForm);
    labelFormSetup();
    buttonGroupSetup();
})


var files,
    label_type,
    upload_prompt_div = $('#upload-section'),
    upload_results_div = $('#upload-results'),
    results_div = upload_results_div.find('#results'),
    error_div = $('#error-message-box'),
    logo_nav = $('.navbar-brand'),
    back_nav = $('li.nav-back');