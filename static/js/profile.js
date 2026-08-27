// ===========================================
// Profile Page JavaScript
// ===========================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("Profile Loaded Successfully");

    // ===========================================
    // Animate Numbers
    // ===========================================

    const numbers = document.querySelectorAll(
        ".mini-stat h2, .summary-box h4"
    );

    numbers.forEach((num) => {

        let text = num.innerText;

        let value = parseInt(text);

        if (!isNaN(value)) {

            let current = 0;

            let speed = Math.max(1, Math.floor(value / 40));

            let counter = setInterval(() => {

                current += speed;

                if (current >= value) {

                    current = value;

                    clearInterval(counter);

                }

                if (text.includes("%")) {

                    num.innerHTML = current + "%";

                }

                else if (text.includes("#")) {

                    num.innerHTML = "#" + current;

                }

                else {

                    num.innerHTML = current;

                }

            }, 20);

        }

    });

    // ===========================================
    // Search Function
    // ===========================================

    const search = document.querySelector(".search-box input");

    if (search) {

        search.addEventListener("keyup", function () {

            const value = this.value.toLowerCase();

            document.querySelectorAll(".history-table tbody tr").forEach((row) => {

                row.style.display =
                    row.innerText.toLowerCase().includes(value)
                        ? ""
                        : "none";

            });

        });

    }

    // ===========================================
    // Card Hover Animation
    // ===========================================

    document.querySelectorAll(
        ".info-card,.summary-box,.achievement-box"
    ).forEach(card => {

        card.addEventListener("mouseenter", () => {

            card.style.transform = "translateY(-8px)";

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform = "translateY(0px)";

        });

    });

    // ===========================================
    // Fade In Animation
    // ===========================================

    document.querySelectorAll(
        ".profile-card,.info-card,.performance-card,.history-card,.achievement-card"
    ).forEach((element, index) => {

        element.style.opacity = "0";

        element.style.transform = "translateY(30px)";

        setTimeout(() => {

            element.style.transition = ".6s";

            element.style.opacity = "1";

            element.style.transform = "translateY(0)";

        }, index * 150);

    });

}); 
// ==========================
// Logout Popup
// ==========================

const logoutBtn = document.getElementById("logoutBtn");
const logoutModal = document.getElementById("logoutModal");
const cancelLogout = document.getElementById("cancelLogout");

if(logoutBtn){

logoutBtn.addEventListener("click",function(e){

e.preventDefault();

logoutModal.style.display="flex";

});

}

if(cancelLogout){

cancelLogout.addEventListener("click",function(){

logoutModal.style.display="none";

});

}

window.onclick=function(e){

if(e.target==logoutModal){

logoutModal.style.display="none";

}

}