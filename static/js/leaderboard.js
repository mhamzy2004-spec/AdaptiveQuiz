// ==========================================
// Leaderboard JavaScript
// ==========================================

document.addEventListener("DOMContentLoaded", function () {
    console.log("Leaderboard Loaded Successfully");

    initializeSearch();
    initializeRefresh();
    initializeChart();
    highlightTopThree();
    initializeAnimations(); // <--- New Animation Engine Added
    setupLogoutModal();
});


// ==========================================
// Search Student
// ==========================================
function initializeSearch() {
    const searchBox = document.getElementById("searchStudent");
    if (!searchBox) return;

    searchBox.addEventListener("keyup", function () {
        const value = this.value.toLowerCase();
        const rows = document.querySelectorAll(".leaderboard-table tbody tr");

        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            if (text.includes(value)) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    });
}


// ==========================================
// Refresh Button
// ==========================================
function initializeRefresh() {
    const refreshBtn = document.querySelector(".refresh-btn");
    if (!refreshBtn) return;

    refreshBtn.addEventListener("click", function () {
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
        setTimeout(() => {
            location.reload();
        }, 800);
    });
}


// ==========================================
// Performance Chart
// ==========================================
function initializeChart() {
    const canvas = document.getElementById("leaderboardChart");
    if (!canvas) return;

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: ["OOP", "DSA", "DBMS", "OS", "CN"],
            datasets: [{
                label: "Average Score",
                data: [88, 92, 80, 84, 95],
                borderWidth: 2,
                borderRadius: 8,
                backgroundColor: "rgba(91, 79, 255, 0.85)", // Premium violet theme color
                borderColor: "#5B4FFF"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}


// ==========================================
// Highlight Top 3
// ==========================================
function highlightTopThree() {
    const rows = document.querySelectorAll(".leaderboard-table tbody tr");
    rows.forEach((row, index) => {
        if (index === 0) {
            row.style.background = "#fff8dc";
        }
        if (index === 1) {
            row.style.background = "#f4f4f4";
        }
        if (index === 2) {
            row.style.background = "#fdf1e7";
        }
    });
}


// ==========================================
// JS Animation System (Winners, Stats & Table)
// ==========================================
function initializeAnimations() {
    
    // --- 1. Stat Cards Number Counting ---
    const statsCounters = document.querySelectorAll('.stat-card h3');
    statsCounters.forEach(counter => {
        const textValue = counter.innerText.trim();
        const hasPercent = textValue.includes('%');
        const hasRank = textValue.includes('#');
        
        // Number nikalne ke liye regex
        let target = parseInt(textValue.replace(/[^0-9]/g, ''), 10);
        if (isNaN(target)) return; 

        let start = 0;
        const duration = 1500; // 1.5 Seconds duration
        const startTime = performance.now();

        function updateNumber(currentTime) {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            
            // Ease-out curve for natural deceleration
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const currentValue = Math.floor(easeProgress * target);
            
            if (hasRank) {
                counter.innerText = `#${currentValue}`;
            } else if (hasPercent) {
                counter.innerText = `${currentValue}%`;
            } else {
                counter.innerText = currentValue.toLocaleString();
            }

            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            } else {
                counter.innerText = textValue; // Correct final value precision
            }
        }
        requestAnimationFrame(updateNumber);
    });

    // --- 2. Winner Cards Delayed Cascade Entrance ---
    const winnerCards = document.querySelectorAll('.winner-card');
    winnerCards.forEach(card => {
        let delay = 300;
        // First/Gold standard attention grabs first, then others
        if (card.classList.contains('gold')) delay = 150;
        if (card.classList.contains('silver')) delay = 350;
        if (card.classList.contains('bronze')) delay = 550;

        setTimeout(() => {
            card.classList.add('animate-show');
        }, delay);
    });

    // --- 3. Table Rows Smooth Reveal ---
    const tableRows = document.querySelectorAll('.leaderboard-table tbody tr');
    tableRows.forEach((row, index) => {
        setTimeout(() => {
            row.classList.add('animate-show');
        }, 200 + (index * 60)); // Har row thora sequence gap le kar slide up hogi
    });

    // --- 4. Auto Scroll To Current User (Triggered post table reveal) ---
    const currentUser = document.querySelector(".current-user");
    if (currentUser) {
        setTimeout(() => {
            currentUser.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });
        }, 1000); // 1 second delay so user sees table flow first
    }
}


// ==========================================
// Logout Popup Modal
// ==========================================
function setupLogoutModal() {
    const logoutBtn = document.getElementById("logoutBtn");
    const logoutModal = document.getElementById("logoutModal");
    const cancelLogout = document.getElementById("cancelLogout");

    if (logoutBtn) {
        logoutBtn.addEventListener("click", function (e) {
            e.preventDefault();
            if (logoutModal) logoutModal.style.display = "flex";
        });
    }

    if (cancelLogout) {
        cancelLogout.addEventListener("click", function () {
            if (logoutModal) logoutModal.style.display = "none";
        });
    }

    window.onclick = function (e) {
        if (e.target == logoutModal) {
            logoutModal.style.display = "none";
        }
    };
}