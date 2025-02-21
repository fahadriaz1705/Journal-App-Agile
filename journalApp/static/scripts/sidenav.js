var navopen = false;
function nav() {
    if (!navopen) {
        document.getElementById("mySidebar").style.width = "250px";
        document.getElementById("main").style.marginLeft = "250px";
        document.getElementById("mySidebar").style.left = "10px";
        navopen = true;
    }
    else {
        document.getElementById("mySidebar").style.width = "0";
        document.getElementById("main").style.marginLeft = "0";
        document.getElementById("mySidebar").style.left = "-30px";
        navopen = false;
    }
}