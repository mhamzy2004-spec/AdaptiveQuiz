// ======================================================
// Result Page JavaScript
// Adaptive Quiz Generator
// ======================================================

document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // Percentage Counter Animation
    // ==========================================

    const counter = document.getElementById("percentageCounter");

    if (counter) {

        let finalValue = parseInt(counter.innerText);

        if (isNaN(finalValue)) {

            finalValue = 0;

        }

        let current = 0;

        counter.innerText = "0%";

        const speed = 20;

        const timer = setInterval(function () {

            current++;

            counter.innerText = current + "%";

            if (current >= finalValue) {

                clearInterval(timer);

            }

        }, speed);

    }

    // ==========================================
    // Progress Bar Animation
    // ==========================================

    const progressBar = document.getElementById("progressBar");

    if (progressBar) {

        const targetWidth = progressBar.style.width;

        progressBar.style.width = "0%";

        setTimeout(function () {

            progressBar.style.width = targetWidth;

        }, 600);

    }

    // ==========================================
    // Fade-in Animation
    // ==========================================

    const cards = document.querySelectorAll(

        ".result-card, .analysis-card, .recommendation-card, .summary-card"

    );

    cards.forEach(function (card, index) {

        card.style.opacity = "0";

        card.style.transform = "translateY(40px)";

        setTimeout(function () {

            card.style.transition = "0.8s ease";

            card.style.opacity = "1";

            card.style.transform = "translateY(0px)";

        }, index * 180);

    });

    // ==========================================
    // Hover Effect
    // ==========================================

    document.querySelectorAll(".result-card").forEach(function (card) {

        card.addEventListener("mouseenter", function () {

            card.style.transform = "translateY(-8px) scale(1.02)";

        });

        card.addEventListener("mouseleave", function () {

            card.style.transform = "translateY(0px) scale(1)";

        });

    });

    // ==========================================
    // AI Recommendation Animation
    // ==========================================

    const recommendation = document.querySelector(".recommendation");

    if (recommendation) {

        recommendation.animate([

            {

                opacity: 0,

                transform: "translateY(30px)"

            },

            {

                opacity: 1,

                transform: "translateY(0px)"

            }

        ], {

            duration: 1200,

            easing: "ease"

        });

    }

    // ==========================================
    // Button Ripple Effect
    // ==========================================

    document.querySelectorAll(".btn").forEach(function (button) {

        button.addEventListener("click", function (e) {

            const circle = document.createElement("span");

            const diameter = Math.max(

                button.clientWidth,

                button.clientHeight

            );

            circle.style.width = diameter + "px";

            circle.style.height = diameter + "px";

            circle.style.left =

                e.offsetX - diameter / 2 + "px";

            circle.style.top =

                e.offsetY - diameter / 2 + "px";

            circle.classList.add("ripple");

            const ripple = button.getElementsByClassName("ripple")[0];

            if (ripple) {

                ripple.remove();

            }

            button.appendChild(circle);

        });

    });

    // ==========================================
    // Confetti Effect (90%+)
    // ==========================================

    const percentageText = document.getElementById("percentageCounter");

    if (percentageText) {

        const value = parseInt(percentageText.textContent);

        if (value >= 90) {

            confettiAnimation();

        }

    }

});


// ======================================================
// Confetti
// ======================================================

function confettiAnimation() {

    for (let i = 0; i < 80; i++) {

        const confetti = document.createElement("div");

        confetti.style.position = "fixed";

        confetti.style.left = Math.random() * 100 + "%";

        confetti.style.top = "-20px";

        confetti.style.width = "10px";

        confetti.style.height = "10px";

        confetti.style.borderRadius = "50%";

        confetti.style.background =
            "hsl(" + Math.random() * 360 + ",80%,60%)";

        confetti.style.zIndex = "9999";

        confetti.style.pointerEvents = "none";

        document.body.appendChild(confetti);

        const duration =

            2500 + Math.random() * 2500;

        confetti.animate([

            {

                transform: "translateY(0px) rotate(0deg)",

                opacity: 1

            },

            {

                transform:
                    "translateY(100vh) rotate(720deg)",

                opacity: 0

            }

        ], {

            duration: duration,

            easing: "linear"

        });

        setTimeout(function () {

            confetti.remove();

        }, duration);

    }

}