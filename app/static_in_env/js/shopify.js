    const sizeBtn = document.getElementById('size_guide');
    const sizearrow = document.getElementById("size_arrow");
    const sizearrow_fill = document.getElementById("size_arrow_fill");
    const fabricBtn = document.getElementById('fabric');
    const fabricarrow = document.getElementById("fabric_arrow");
    const fabricarrow_fill = document.getElementById("fabric_arrow_fill");

    sizeBtn.addEventListener("click", function() {
            if (sizearrow.style.display === "none") {
                sizearrow.style.display = "block";
                sizearrow_fill.style.display = "none";
            } else {
                sizearrow.style.display = "none";
                sizearrow_fill.style.display = "block";
            }
        },

        fabricBtn.addEventListener("click", function() {
                if (fabricarrow.style.display === "none") {
                    fabricarrow.style.display = "block";
                    fabricarrow_fill.style.display = "none";
                } else {
                    fabricarrow.style.display = "none";
                    fabricarrow_fill.style.display = "block";
                }
            }

        ));