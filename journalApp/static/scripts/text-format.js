// Function to apply text formatting (Bold, Italic, Underline)
function formatText(command) {
    document.execCommand(command, false, null);
}

// Function to change text alignment (Left, Center, Right)
function changeAlignment(alignment) {
    document.getElementById("journalContent").style.textAlign = alignment;
}

// Function to change font size
function changeSize(size) {

    const text = document.getElementById("journalContent");
    let fontSize = window.getComputedStyle(text).fontSize; // Get the font size of the document
    fontSize = parseInt(fontSize); // Separate the integer part of the font size

    if (size == 'up') { // If the font increase button is pressed,
        if (fontSize < 50) {
            fontSize += 2; // The font size increases at an increment of 2
        }
    }
    else { // Else, the font decrease button would've been pressed,
        if (fontSize > 4) {
            fontSize -= 2; // Decreasing the font size at an increment of 2
        }
    }

    fontSize = fontSize + 'px'; // Adding the font size unit to the string
    text.style.fontSize = fontSize; // Applying the font size to the journal entry
}

// Function to download the journal entry as a text file
// this function is inspired by: https://stackoverflow.com/questions/13685263/can-i-save-input-from-form-to-txt-in-html-using-javascript-jquery-and-then-us
function downloadJournal() {

    const entry = document.getElementById("journalContent").innerText;

    const blob = new Blob([entry], { type: "text/plain" }); // Convert the text from an array format to a plain text format

    const link = document.createElement("a"); // Creat a link to represent the blob in order to download it
    link.href = URL.createObjectURL(blob);

    let filename = 'ThoughtThread-Journal-' + `${document.getElementById('journalTitle').value}.txt`; // Setting the journal entry's title as the file name
    filename = filename.replaceAll(' ', '_');
    link.download = filename;
    link.click(); // Saving the file on click of the button
}

// Function to add Bullet Points to the journal entry 
function addLists(type) {

    var journal = document.getElementById('journalContent');

    // Access the user selected text and its range
    var selection = window.getSelection();
    var range = selection.getRangeAt(0);

    // Convert the selected text into a string format for manipulating the data 
    var selectedText = selection.toString();

    // If any text has been selected 
    if (selectedText) {

        // Split the selected text into lines and store as an array 
        var lines = selectedText.split('\n');

        // If the content is a list, remove the list elements, else add the list elements
        var newText = stringMani(lines, type);

        // Delete the contents inside the selected range
        range.deleteContents();

        // Due to the formatting of the text, a new division is created, inside of which the new list is added
        var bulletListElement = document.createElement("div");
        bulletListElement.innerHTML = newText;
        range.insertNode(bulletListElement);
    }

    // If there isn't any selected text, list format will be applied to the whole journal entry
    else {

        var lines = journal.innerText.split('\n');
        var newText = stringMani(lines, type);
        journal.innerHTML = newText;
    }

    journal.focus();
}

// The following function manipulated the strings from the journal entries
function stringMani(lines, prefix) {

    let changedText = '';

    // A for loop iterates for all the lines of a journal entry
    for (let i = 0; i < lines.length; i++) {

        // The temp variable is an empty string upon each iteration
        let temp = '';

        // First check if there is bullet or numbered points
        if (lines[i][0] == '•' || (lines[i][0] >= 0 && lines[i][0] <= 9)) {

            // To get rid of the type of list, we count the number of characters to remove form the line
            let count = 0;

            // For a bullet point, the number of characters to remove is fixed
            if (lines[i][0] == '•') {
                count = 2;
            }
            // For numbered lists,
            else {
                count = parseInt(lines[i]); // Extract the number from the list
                count = count.toString().length + 1; // Get the number of characters in that number and add one, which considers the number, the '.', and the space
                count = parseInt(count); // Convert the value back to integer
            }

            // While the line is not the last line, 
            if (i < lines.length - 1) {

                // Remove the beginning characters from the string according to the count value, and add the break tag
                temp = lines[i].substring(count, lines[i].length) + '<br>';
            }
            else {
                // Remove the beginning characters from the string according to the count value
                temp = lines[i].substring(count, lines[i].length);
            }
        }
        else {

            // If the user wants to add a bullet point to the list
            if (prefix == 'bullet') {

                // While it is not the last line, 
                if (i < lines.length - 1) {
                    // Add the bullet point and the break tag to the string
                    temp = '• ' + lines[i] + '<br>';
                }
                // If it is the last line
                else {
                    // Only add the bullet point to the string
                    temp = '• ' + lines[i];
                }
            }
            // If the user wants to add a numbered list
            else {

                // Create a string with the index value of the line
                let index = i + 1;
                index = index.toString() + '. ';

                // While it is not the last line, 
                if (i < lines.length - 1) {

                    // Add the number point and the break tag to the string
                    temp = index + lines[i] + '<br>';
                }
                // If it is the last line
                else {
                    // Add the number point to the string
                    temp = index + lines[i];
                }
            }
        }

        // Add the modified string to the variable.
        changedText += temp;
    }

    return changedText;
}

// Showing tag options
/* let options = false;
function showOptions() {
    if (!options) {
        document.getElementById('existingTag').style.display = 'block';
        options = true;
    }
    else {
        document.getElementById('existingTag').style.display = 'none';
        options = false;
    }
}
 */
// Add new tag pop up
/* let add = false;
function addTag() {
    if (!add) {
        document.getElementById('newtag').style.display = 'block';
        add = true;
    }
    else {
        document.getElementById('newtag').style.display = 'none';
        add = false;
    }
} */

// Add attachment
/* let attachment = false;
function addAttachments() {
    if (!attachment) {
        document.getElementById('attachments-block').style.display = 'block';
        attachment = true;
    }
    else {
        document.getElementById('attachments-block').style.display = 'none';
        attachment = false;
    }
} */