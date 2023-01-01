
var group_select = document.getElementById("group");
var students_select = document.getElementById("students");
var window_location = window.location.href;
var activity_id = window_location.slice(-1)

group_select.onchange = function() {
    group = group_select.value;

    fetch('/grade-activity/' + activity_id + '/' + group).then(function(response) {
        response.json().then(function(data) {
            var optionHTML = '';

            for (var student of data.students) {
                optionHTML += '<option value="' + student.id + '">' + student.name + '</option>';
            }
            students_select.innerHTML = optionHTML;
        })
    })

};



