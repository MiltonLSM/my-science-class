
// -----------------SHOW STUDENTS ACCORDING TO THE GROUP-----------------

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


// --------------------CALCULATE AND SHOW THE TOTAL SCORE ------------------

var totalScore = document.getElementById("total-score")

var itemPoints = document.getElementsByClassName("item-points");
var itemWeights = document.getElementsByClassName("item-weight");


function changeScore() {
    var score = 0;

    for (let i = 0; i < itemPoints.length; i++) {
        var itemScore = (Number(itemWeights[i].innerHTML)/100) * Number(itemPoints[i].value);
        score += itemScore;
    };

    totalScore.innerHTML = score.toFixed(2);
}


// ---------------------FILTER THE ROPORT BY GROUP --------------------------

var group_report = document.getElementById("5B");

function chooseGroup() {
    
    console.log(group_report);
}



// group_report.onclick = function() {

// }


