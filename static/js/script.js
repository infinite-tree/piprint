function show_error_message(error_message){
    var error_msg_div = $('#error_message_box p');
    error_msg_div.text(error_message);
    error_div.show();
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
}


$(document).ready(function(){
    // $('form').on('submit', submitForm);
    $('input[type=file]').on('change', prepareUpload);
    $('.nav-back').click(restoreForm);
})


var files,
    upload_prompt_div = $('#upload-section'),
    upload_results_div = $('#upload-results'),
    results_div = upload_results_div.find('#results'),
    error_div = $('#error_message_box'),
    logo_nav = $('.navbar-brand'),
    back_nav = $('li.nav-back');