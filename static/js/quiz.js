document.addEventListener("DOMContentLoaded", function () {
    // UI Screen Navigation Targets
    const showInstructionsBtn = document.getElementById("showInstructions");
    const cancelQuizBtn = document.getElementById("cancelQuiz");
    const startQuizNowBtn = document.getElementById("startQuizNow");
    
    const heroSection = document.getElementById("heroSection");
    const instructionScreen = document.getElementById("instructionScreen");
    const quizSection = document.getElementById("quizSection");

    // Dynamic Execution Trackers
    let currentIdx = 1;
    const questionCards = document.querySelectorAll(".question-card-item");
    const totalQuestions = questionCards.length;

    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const submitQuizBtn = document.getElementById("submitQuizBtn");
    const finalSubmitBtn = document.getElementById("finalSubmitBtn");
    const quizForm = document.getElementById("quizForm");
    const timeInput = document.getElementById("time_taken_input");

    // Timer Variables
    let totalTimeSeconds = 10 * 60; // 10 Minutes Allocation
    let timeElapsed = 0;
    let countdownInterval;

    // --- Screen State Control Handlers ---
    if (showInstructionsBtn) {
        showInstructionsBtn.addEventListener("click", () => {
            instructionScreen.style.display = "flex";
        });
    }

    if (cancelQuizBtn) {
        cancelQuizBtn.addEventListener("click", () => {
            instructionScreen.style.display = "none";
        });
    }

    if (startQuizNowBtn) {
        startQuizNowBtn.addEventListener("click", () => {
            instructionScreen.style.display = "none";
            heroSection.style.display = "none";
            quizSection.style.display = "block";
            startQuizTimer();
            updateNavigationContext();
        });
    }

    // --- Radio Options Row Highlight Interaction ---
    document.querySelectorAll(".option-wrapper-premium").forEach(wrapper => {
        const radioInput = wrapper.querySelector(".option-radio-custom");
        
        wrapper.addEventListener("click", function (e) {
            if (e.target !== radioInput) {
                radioInput.checked = true;
                // Form action update callback directly triggers handling change
                radioInput.dispatchEvent(new Event("change", { bubbles: true }));
            }
        });
    });

    // Reactive listener tracking checking selection events
    quizForm.addEventListener("change", function (e) {
        if (e.target && e.target.classList.contains("option-radio-custom")) {
            const currentCard = e.target.closest(".question-card-item");
            
            // Clean legacy wrapper selections inside current contextual card block
            currentCard.querySelectorAll(".option-wrapper-premium").forEach(el => {
                el.classList.remove("active-checked-state");
            });

            // Apply selected highlight tracking premium layout rules
            if (e.target.checked) {
                e.target.closest(".option-wrapper-premium").classList.add("active-checked-state");
            }

            // Sync visual palette trackers
            markPaletteAnswered(currentIdx);
        }
    });

    // --- Palette Button Direct Jumps Click Framework ---
    document.querySelectorAll(".palette-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const targetIdx = parseInt(this.getAttribute("data-target"));
            navigateToQuestion(targetIdx);
        });
    });

    function navigateToQuestion(targetIdx) {
        if (targetIdx >= 1 && targetIdx <= totalQuestions) {
            questionCards.forEach(card => card.style.display = "none");
            document.querySelector(`.question-card-item[data-question="${targetIdx}"]`).style.display = "block";
            currentIdx = targetIdx;
            updateNavigationContext();
        }
    }

    // --- Core Navigation Step Controls ---
    nextBtn.addEventListener("click", () => {
        if (currentIdx < totalQuestions) {
            navigateToQuestion(currentIdx + 1);
        }
    });

    prevBtn.addEventListener("click", () => {
        if (currentIdx > 1) {
            navigateToQuestion(currentIdx - 1);
        }
    });

    // --- UI Context Synchronizer ---
    function updateNavigationContext() {
        // Manage Previous/Next visibility boundaries
        prevBtn.style.visibility = (currentIdx === 1) ? "hidden" : "visible";
        
        if (currentIdx === totalQuestions) {
            nextBtn.style.display = "none";
            submitQuizBtn.style.display = "inline-block";
        } else {
            nextBtn.style.display = "inline-block";
            submitQuizBtn.style.display = "none";
        }

        // Update textual metadata elements
        document.getElementById("currentQuestion").innerText = currentIdx;
        
        // Render dynamic progress bars width calculations (Fixed to hit 100% properly)
        const progressPercent = Math.round((currentIdx / totalQuestions) * 100);
        document.getElementById("progressBar").style.width = `${progressPercent}%`;
        document.getElementById("progressPercent").innerText = `${progressPercent}%`;

        // Sync highlighting on active sidebar palette trackers
        document.querySelectorAll(".palette-btn").forEach(btn => {
            btn.classList.remove("current-active");
            if (parseInt(btn.getAttribute("data-target")) === currentIdx) {
                btn.classList.add("current-active");
            }
        });
    }

    function markPaletteAnswered(index) {
        const correspondingBtn = document.querySelector(`.palette-btn[data-target="${index}"]`);
        if (correspondingBtn) {
            correspondingBtn.classList.add("answered-state");
        }
    }

    // --- System Countdown Timer ---
    function startQuizTimer() {
        const timerDisplay = document.getElementById("timer");

        countdownInterval = setInterval(() => {
            if (totalTimeSeconds <= 0) {
                clearInterval(countdownInterval);
                autoSubmitQuiz();
                return;
            }

            totalTimeSeconds--;
            timeElapsed++;
            
            // Real-time value capture
            if (timeInput) {
                timeInput.value = timeElapsed;
            }

            let minutes = Math.floor(totalTimeSeconds / 60);
            let seconds = totalTimeSeconds % 60;

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            timerDisplay.innerText = `${minutes}:${seconds}`;

            // Red alerts warning when remaining time under 60 seconds
            if (totalTimeSeconds <= 60) {
                timerDisplay.parentElement.style.background = "#dc3545";
                timerDisplay.parentElement.style.color = "#ffffff";
            }
        }, 1000);
    }

    // --- Form Submissions Handler ---
    const bootstrapSubmitModal = new bootstrap.Modal(document.getElementById('submitModal'));
    
    submitQuizBtn.addEventListener("click", () => {
        bootstrapSubmitModal.show();
    });

    finalSubmitBtn.addEventListener("click", () => {
        clearInterval(countdownInterval);
        bootstrapSubmitModal.hide();
        
        // Final fallback block ensuring time is locked inside the form
        if (timeInput) {
            timeInput.value = timeElapsed;
        }
        
        quizForm.submit();
    });

    function autoSubmitQuiz() {
        alert("Time is up! Your quiz will be automatically submitted.");
        
        // Locking last tracked state context
        if (timeInput) {
            timeInput.value = timeElapsed;
        }
        
        quizForm.submit();
    }
});