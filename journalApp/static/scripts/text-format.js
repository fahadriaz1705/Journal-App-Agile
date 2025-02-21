// Function to apply text formatting (Bold, Italic, Underline)
function formatText(command) {
    document.execCommand(command, false, null);
}

// Function to change text alignment (Left, Center, Right)
function changeAlignment(alignment) {
    document.getElementById("journalEntry").style.textAlign = alignment;
}

// Function to change font size
function changeSize(size) {

    const text = document.getElementById("journalEntry");
    let fontSize = window.getComputedStyle(text).fontSize;
    fontSize = parseInt(fontSize);

    if (size == 'up') {
        fontSize += 2;
    }
    else {
        fontSize -= 2;
    }

    fontSize = fontSize + 'px';
    text.style.fontSize = fontSize;
}

// Function to download the journal entry as a text file
function downloadJournal() {
    const entry = document.getElementById("journalEntry").innerText;
    // convert the text from an array format to a text format
    const blob = new Blob([entry], { type: "text/plain" });
    //creating a link to represent the blob inorder to download it
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    // setting the file name as the name of the title of the entry
    let filename = `${document.getElementById('journalTitle').value}.txt`;
    link.download = filename;
    link.click();
}

// Bullet Points function 
function insertBulletList() {

    var journal = document.getElementById('journalEntry');

    // get the current selection of text and its range
    var selection = window.getSelection();
    var range = selection.getRangeAt(0);

    var selectedText = selection.toString(); // convert text to string

    // If any text has been selected 
    if (selectedText) {

        // Split the selected text into lines and store as an array 
        var lines = selectedText.split('\n');

        // The strings are then changed to add bullet points
        var newText = '';

        // A loop iterates for each line
        for (var i = 0; i < lines.length; i++) {

            // The temp variable changes the string by adding the bullet points and the <br> tag to ensure when its displayed in the <div> it is displayed as separate lines
            var temp = `• ` + lines[i] + '<br>';

            // Add the changed line to the newText string
            newText += temp;
        }

        // delete the contents inside the selected range
        range.deleteContents();

        // due to the formatting of the text, a new division is created, inside of which the new bullet point list is added
        var bulletListElement = document.createElement("div");
        bulletListElement.innerHTML = newText;
        range.insertNode(bulletListElement);

    }
    // if there isn't any selected text, bullet points will be applied to the whole journal entry
    else {
        var lines = journal.innerText.split('\n');
        var newText = '';
        for (var i = 0; i < lines.length; i++) {
            var temp = `• ` + lines[i] + '<br>';
            newText += temp;
        }
        journal.innerHTML = newText;
    }

    journal.focus();
}


// Insert Numbered List at the cursor position
function insertNumberedList() {
    const journal = document.getElementById('journalEntry');

    // Get the current selection and the current cursor position
    const selection = window.getSelection();
    const range = selection.getRangeAt(0);
    const selectedText = selection.toString();
    const lines = (selectedText || journal.innerText).split('\n');
    let newText = '';

    // Add numbering to each line of the selected text or all text
    lines.forEach((line, index) => {
        newText += `<div>${index + 1}. ${line.trim()}</div>`;
    });

    // Clear the current selection and insert the numbered list
    range.deleteContents();
    range.insertNode(document.createRange().createContextualFragment(newText));
    journal.focus();
}