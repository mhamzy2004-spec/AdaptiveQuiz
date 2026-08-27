// ==========================================
// Subject Selection JS
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    // ===============================
    // Page Fade Animation
    // ===============================

    document.body.style.opacity = "0";

    setTimeout(() => {

        document.body.style.transition = "opacity .7s ease";

        document.body.style.opacity = "1";

    }, 100);


    // ===============================
    // Animate Subject Cards
    // ===============================

    const cards = document.querySelectorAll(".subject-card");

    cards.forEach((card, index) => {

        card.style.opacity = "0";
        card.style.transform = "translateY(40px)";

        setTimeout(() => {

            card.style.transition = ".6s ease";

            card.style.opacity = "1";
            card.style.transform = "translateY(0)";

        }, index * 120);

    });


    // ===============================
    // Search Subject
    // ===============================

    const search = document.querySelector(".search-box input");

    if (search) {

        search.addEventListener("keyup", function () {

            let value = this.value.toLowerCase();

            document.querySelectorAll(".subject-card").forEach(card => {

                let subject = card.querySelector("h3").innerText.toLowerCase();

                if (subject.includes(value)) {

                    card.style.display = "block";

                } else {

                    card.style.display = "none";

                }

            });

        });

    }


    // ===============================
    // Card Hover Animation
    // ===============================

    cards.forEach(card => {

        card.addEventListener("mouseenter", () => {

            card.style.transform = "translateY(-10px) scale(1.03)";

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform = "translateY(0) scale(1)";

        });

    });


    // ===============================
    // Button Click Animation
    // ===============================

    document.querySelectorAll(".start-btn").forEach(btn => {

        btn.addEventListener("click", function () {

            this.innerHTML =
                '<i class="fas fa-spinner fa-spin"></i> Loading...';

        });

    });


    // ===============================
    // Recommendation Button
    // ===============================

    const recommend = document.querySelector(".recommendation-btn");

    if (recommend) {

        recommend.addEventListener("mouseenter", function () {

            this.style.transform = "scale(1.05)";

        });

        recommend.addEventListener("mouseleave", function () {

            this.style.transform = "scale(1)";

        });

    }


    // ===============================
    // Progress Circle Animation
    // ===============================

    const progress = document.querySelector(".progress-circle h2");

    if (progress) {

        let target = parseInt(progress.innerText);

        let count = 0;

        progress.innerText = "0%";

        let interval = setInterval(() => {

            count++;

            progress.innerText = count + "%";

            if (count >= target)

                clearInterval(interval);

        }, 20);

    }


    // ===============================
    // Logout Modal
    // ===============================

    const logoutBtn = document.getElementById("logoutBtn");
    const logoutModal = document.getElementById("logoutModal");
    const cancelLogout = document.getElementById("cancelLogout");

    if (logoutBtn) {

        logoutBtn.addEventListener("click", function (e) {

            e.preventDefault();

            logoutModal.classList.add("active");

        });

    }

    if (cancelLogout) {

        cancelLogout.addEventListener("click", function () {

            logoutModal.classList.remove("active");

        });

    }

    window.addEventListener("click", function (e) {

        if (e.target === logoutModal) {

            logoutModal.classList.remove("active");

        }

    });

});


// ==========================================
// Smooth Scroll
// ==========================================

window.scroll({

    top: 0,

    behavior: "smooth"

});


// ==========================================
// Console
// ==========================================

console.log("✅ Subject Selection Loaded Successfully");