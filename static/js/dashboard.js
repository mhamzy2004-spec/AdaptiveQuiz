document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // Recent Results Chart
    // =====================================

    const ctx = document.getElementById("resultChart");

    if (ctx) {

        const gradient = ctx.getContext("2d").createLinearGradient(0,0,0,400);

        gradient.addColorStop(0,"rgba(91,79,255,.35)");
        gradient.addColorStop(1,"rgba(91,79,255,.02)");

        new Chart(ctx,{

            type:"line",

            data:{

                labels: chartLabels,

                datasets:[{

                    label:"Quiz Score (%)",

                    data: chartScores,

                    borderColor:"#5B4FFF",

                    backgroundColor:gradient,

                    borderWidth:4,

                    tension:.45,

                    fill:true,

                    pointBackgroundColor:"#ffffff",

                    pointBorderColor:"#5B4FFF",

                    pointBorderWidth:3,

                    pointRadius:6,

                    pointHoverRadius:9

                }]

            },

            options:{

                responsive:true,

                maintainAspectRatio:false,

                interaction:{

                    intersect:false,

                    mode:"index"

                },

                plugins:{

                    legend:{

                        display:false

                    },

                    tooltip:{

                        backgroundColor:"#1F2937",

                        titleColor:"#fff",

                        bodyColor:"#fff",

                        displayColors:false,

                        padding:12,

                        callbacks:{

                            label:function(context){

                                return context.raw+"%";

                            }

                        }

                    }

                },

                scales:{

                    x:{

                        grid:{

                            display:false

                        },

                        ticks:{

                            color:"#6B7280"

                        }

                    },

                    y:{

                        beginAtZero:true,

                        max:100,

                        ticks:{

                            color:"#6B7280",

                            callback:function(value){

                                return value+"%";

                            }

                        },

                        grid:{

                            color:"rgba(0,0,0,.05)"

                        }

                    }

                },

                animation:{

                    duration:1800,

                    easing:"easeOutQuart"

                }

            }

        });

    }

    // =====================================
    // Search Animation
    // =====================================

    const searchInput=document.querySelector(".search-box input");
    const searchBox=document.querySelector(".search-box");

    if(searchInput && searchBox){

        searchInput.addEventListener("focus",()=>{

            searchBox.style.boxShadow="0 5px 20px rgba(91,79,255,.18)";
            searchBox.style.borderColor="#5B4FFF";

        });

        searchInput.addEventListener("blur",()=>{

            searchBox.style.boxShadow="0 4px 10px rgba(0,0,0,.03)";
            searchBox.style.borderColor="transparent";

        });

    }

    // =====================================
    // Start Quiz Buttons
    // =====================================

    document.querySelectorAll(".start-btn").forEach(btn=>{

        btn.addEventListener("click",function(){

            console.log("Opening Quiz...");

        });

    });

    // =====================================
    // Assessment Button
    // =====================================

    const assessmentBtn=document.querySelector(".assessment-btn");

    if(assessmentBtn){

        assessmentBtn.addEventListener("click",()=>{

            console.log("Assessment Started");

        });

    }

});


// =====================================
// Logout Popup
// =====================================

const logoutBtn=document.getElementById("logoutBtn");

const logoutModal=document.getElementById("logoutModal");

const cancelLogout=document.getElementById("cancelLogout");

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

    if(e.target===logoutModal){

        logoutModal.style.display="none";

    }

};