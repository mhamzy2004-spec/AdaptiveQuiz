let currentIndex = 0;
// Array to track user selections matching questions index mapping arrays
let userAnswers = new Array(questions.length).fill(null); 
let timerInterval = null;
let totalTime = 600; // 10 minutes in seconds

/*=========================================
        DOM ELEMENTS
=========================================*/
const questionNum = document.getElementById("questionNum");
const categoryBadge = document.getElementById("categoryBadge");
const questionText = document.getElementById("questionText");
const optionsContainer = document.getElementById("optionsContainer");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const paletteGrid = document.getElementById("paletteGrid");
const timerDisplay = document.getElementById("timerDisplay");

/*=========================================
        RENDER INTERFACE
=========================================*/
function initQuiz() {
    if (questions.length === 0) {
        alert("No questions loaded from database! Please check table rows data content.");
        return;
    }
    renderPalette();
    loadQuestion(currentIndex);
    startTimer();
}

function loadQuestion(index) {
    currentIndex = index;
    const currentQ = questions[index];

    questionNum.innerText = `Question ${index + 1}/${questions.length}`;
    categoryBadge.innerHTML = `<i class="fas fa-code"></i> ${currentQ.subject}`;
    questionText.innerText = currentQ.question;

    optionsContainer.innerHTML = "";
    
    // Dynamic array mapping containing 4 option columns fields
    const optionsArray = [currentQ.option1, currentQ.option2, currentQ.option3, currentQ.option4];

    optionsArray.forEach((optionText, oIdx) => {
        const div = document.createElement("div");
        div.className = `option-card ${userAnswers[index] === optionText ? 'selected' : ''}`;
        
        // CSS matching system styling classes alignment fixes
        if (userAnswers[index] === optionText) {
            div.style.borderColor = "#6C63FF";
            div.style.background = "#F3F2FF";
        }

        div.innerHTML = `
            <input type="radio" name="answer" id="opt${oIdx}" ${userAnswers[index] === optionText ? 'checked' : ''}>
            <span>${optionText}</span>
        `;
        div.addEventListener("click", () => selectOption(optionText));
        optionsContainer.appendChild(div);
    });

    prevBtn.disabled = index === 0;
    nextBtn.innerHTML = index === questions.length - 1 ? `Review <i class="fas fa-eye"></i>` : `Next <i class="fas fa-arrow-right"></i>`;

    updatePaletteUI();
}

function selectOption(optionText) {
    userAnswers[currentIndex] = optionText;
    loadQuestion(currentIndex); // UI state refresh mechanism
}

function renderPalette() {
    paletteGrid.innerHTML = "";
    questions.forEach((_, index) => {
        const btn = document.createElement("button");
        btn.innerText = index + 1;
        btn.className = "palette-btn unanswered";
        btn.addEventListener("click", () => loadQuestion(index));
        paletteGrid.appendChild(btn);
    });
}

function updatePaletteUI() {
    const buttons = paletteGrid.querySelectorAll("button");
    buttons.forEach((btn, index) => {
        btn.className = "palette-btn";
        if (index === currentIndex) {
            btn.classList.add("active");
            btn.style.background = "#5B4FFF";
            btn.style.color = "white";
        } else if (userAnswers[index] !== null) {
            btn.style.background = "#22c55e";
            btn.style.color = "white";
        } else {
            btn.style.background = "#F3F4F6";
            btn.style.color = "#2d3436";
        }
    });
}

/*=========================================
        TIMER FUNCTION
=========================================*/
function startTimer() {
    timerInterval = setInterval(() => {
        if (totalTime <= 0) {
            clearInterval(timerInterval);
            submitAssessment(); 
            return;
        }
        totalTime--;
        const mins = Math.floor(totalTime / 60);
        const secs = totalTime % 60;
        timerDisplay.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }, 1000);
}

/*=========================================
        NAVIGATION EVENT LISTENERS
=========================================*/
nextBtn.addEventListener("click", () => {
    if (currentIndex < questions.length - 1) {
        loadQuestion(currentIndex + 1);
    }
});

prevBtn.addEventListener("click", () => {
    if (currentIndex > 0) {
        loadQuestion(currentIndex - 1);
    }
});

/*=========================================
        SUBMISSION PROCESSOR PIPELINE
=========================================*/
function submitAssessment() {
    clearInterval(timerInterval);

    // Dynamic map collection initialization tracking exact data parameters { question_id: user_chosen_string }
    let payloadAnswers = {};
    questions.forEach((q, index) => {
        if (userAnswers[index] !== null) {
            payloadAnswers[q.id] = userAnswers[index];
        }
    });

    // 🔥 FIXED: Endpoint badal kar '/assessment' kiya ha jo aapke naye Flask code se match krta ha
    fetch('/assessment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answers: payloadAnswers })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            // Layout views state switches toggles
            document.getElementById("quizWindow").classList.add("d-none");
            document.getElementById("sidebarContainer").classList.add("d-none");

            document.getElementById("finalScore").innerText = `${data.score} / ${data.total}`;
            document.getElementById("finalLevel").innerText = data.level;

            const resultCard = document.getElementById("resultCard");
            resultCard.classList.remove("d-none");
            resultCard.scrollIntoView({ behavior: "smooth" });

            document.getElementById("goToDashboardBtn").onclick = function() {
                // Flask redirect url ko trigger krna
                window.location.href = "/dashboard"; 
            };
        } else {
            alert("Something went wrong during submission: " + data.message);
        }
    })
    .catch(error => {
        console.error('Submission processing failure:', error);
        alert("Database execution completed or connection dropped.");
    });
}

const submitBtn = document.getElementById("submitAssessment");
if (submitBtn) {
    submitBtn.addEventListener("click", () => {
        const modal = new bootstrap.Modal(document.getElementById("submitModal"));
        modal.show();
    });
}

document.getElementById("confirmSubmitBtn").addEventListener("click", () => {
    const modalElement = document.getElementById("submitModal");
    const modal = bootstrap.Modal.getInstance(modalElement);
    if (modal) modal.hide();
    submitAssessment();
});

/*=========================================
     START ASSESSMENT HANDLER (Trigger)
=========================================*/
document.getElementById("startAssessmentBtn").addEventListener("click", () => {
    document.getElementById("heroSection").classList.add("d-none");
    const mainQuizInterface = document.getElementById("mainQuizInterface");
    mainQuizInterface.classList.remove("d-none");
    initQuiz();
});