const button =  document.getElementById("submit");
const display = document.getElementById("display");
const locationField = document.getElementById("location");

function generate() {
    
    button.disabled = true;
    display.style.color = "#000000";
    display.innerHTML = "Generating...";
    
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/generate");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        "color":document.getElementById("color").value,
        "location":locationField.options[locationField.selectedIndex].value
    }));
    xhr.onload = function() {
        let response = JSON.parse(xhr.responseText);
        if (response.error) {
            display.style.color = "#ff0000";
            display.innerHTML = response.error;
        } else display.innerHTML = response.generated;
        button.disabled = false;
    }
}