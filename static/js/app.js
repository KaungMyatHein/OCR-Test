document.addEventListener("DOMContentLoaded", () => {
    // Elements
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const browseBtn = document.getElementById("browseBtn");
    const filePreview = document.getElementById("filePreview");
    const fileName = document.getElementById("fileName");
    const fileSize = document.getElementById("fileSize");
    const removeFile = document.getElementById("removeFile");
    const imagePreview = document.getElementById("imagePreview");
    const previewImage = document.getElementById("previewImage");
    const langSelect = document.getElementById("langSelect");
    const processBtn = document.getElementById("processBtn");
    const progressSection = document.getElementById("progressSection");
    const progressFill = document.getElementById("progressFill");
    const progressText = document.getElementById("progressText");
    const resultsSection = document.getElementById("resultsSection");
    const textOutput = document.getElementById("textOutput");
    const pageTabs = document.getElementById("pageTabs");
    const downloadAllBtn = document.getElementById("downloadAllBtn");
    const copyAllBtn = document.getElementById("copyAllBtn");
    const errorSection = document.getElementById("errorSection");
    const errorMessage = document.getElementById("errorMessage");
    const retryBtn = document.getElementById("retryBtn");

    let selectedFile = null;
    let currentResult = null;

    // --- File Selection ---

    browseBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    dropZone.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Drag & Drop
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    removeFile.addEventListener("click", () => {
        clearFile();
    });

    function handleFileSelect(file) {
        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        filePreview.classList.remove("hidden");
        dropZone.classList.add("hidden");

        // Show image preview for image files
        if (file.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                imagePreview.classList.remove("hidden");
            };
            reader.readAsDataURL(file);
        } else {
            imagePreview.classList.add("hidden");
        }

        processBtn.disabled = false;
        hideResults();
        hideError();
    }

    function clearFile() {
        selectedFile = null;
        fileInput.value = "";
        filePreview.classList.add("hidden");
        dropZone.classList.remove("hidden");
        imagePreview.classList.add("hidden");
        processBtn.disabled = true;
        hideResults();
        hideError();
    }

    // --- OCR Processing ---

    processBtn.addEventListener("click", () => {
        if (!selectedFile) return;
        startOCR();
    });

    retryBtn.addEventListener("click", () => {
        if (!selectedFile) return;
        startOCR();
    });

    async function startOCR() {
        hideError();
        hideResults();
        showProgress();

        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("lang", langSelect.value);

        updateProgress(10, "ဖိုင်ကို Upload လုပ်နေသည်...");

        try {
            updateProgress(30, "OCR ဖြင့် Text ထုတ်ယူနေသည်...");

            const response = await fetch("/api/ocr", {
                method: "POST",
                body: formData,
            });

            updateProgress(80, "ရလဒ်များ ပြင်ဆင်နေသည်...");

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "OCR processing failed");
            }

            updateProgress(100, "ပြီးပါပြီ!");
            currentResult = data;

            setTimeout(() => {
                hideProgress();
                showResults(data);
            }, 500);
        } catch (error) {
            hideProgress();
            showError(error.message);
        }
    }

    // --- Results Display ---

    function showResults(data) {
        resultsSection.classList.remove("hidden");

        if (data.type === "pdf") {
            showPDFResults(data);
        } else {
            showImageResults(data);
        }
    }

    function showImageResults(data) {
        pageTabs.classList.add("hidden");
        textOutput.value = data.text || "(Text မတွေ့ပါ)";
    }

    function showPDFResults(data) {
        // Build tabs
        pageTabs.innerHTML = "";
        pageTabs.classList.remove("hidden");

        // "All Pages" tab
        const allTab = createTab("အားလုံး", -1, true);
        pageTabs.appendChild(allTab);

        data.pages.forEach((page) => {
            const tab = createTab(`စာမျက်နှာ ${page.page}`, page.page, false);
            pageTabs.appendChild(tab);
        });

        // Show all text by default
        showAllPagesText(data);
    }

    function createTab(label, pageNum, active) {
        const tab = document.createElement("button");
        tab.className = "page-tab" + (active ? " active" : "");
        tab.textContent = label;
        tab.dataset.page = pageNum;
        tab.addEventListener("click", () => {
            document.querySelectorAll(".page-tab").forEach((t) => t.classList.remove("active"));
            tab.classList.add("active");

            if (pageNum === -1) {
                showAllPagesText(currentResult);
            } else {
                const page = currentResult.pages.find((p) => p.page === pageNum);
                textOutput.value = page ? page.text || "(Text မတွေ့ပါ)" : "";
            }
        });
        return tab;
    }

    function showAllPagesText(data) {
        const allText = data.pages
            .map((p) => `--- စာမျက်နှာ ${p.page} ---\n\n${p.text}`)
            .join("\n\n");
        textOutput.value = allText || "(Text မတွေ့ပါ)";
    }

    function hideResults() {
        resultsSection.classList.add("hidden");
        textOutput.value = "";
        pageTabs.innerHTML = "";
        currentResult = null;
    }

    // --- Download & Copy ---

    downloadAllBtn.addEventListener("click", () => {
        if (!currentResult) return;
        window.location.href = `/api/download/${currentResult.output_id}`;
    });

    copyAllBtn.addEventListener("click", async () => {
        const text = textOutput.value;
        if (!text) return;

        try {
            await navigator.clipboard.writeText(text);
            const originalHTML = copyAllBtn.innerHTML;
            copyAllBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <polyline points="20 6 9 17 4 12"/>
            </svg> Copied!`;
            copyAllBtn.style.color = "var(--success)";
            setTimeout(() => {
                copyAllBtn.innerHTML = originalHTML;
                copyAllBtn.style.color = "";
            }, 2000);
        } catch {
            // Fallback
            textOutput.select();
            document.execCommand("copy");
        }
    });

    // --- Progress ---

    function showProgress() {
        progressSection.classList.remove("hidden");
        processBtn.querySelector(".btn-text").classList.add("hidden");
        processBtn.querySelector(".btn-loading").classList.remove("hidden");
        processBtn.disabled = true;
    }

    function hideProgress() {
        progressSection.classList.add("hidden");
        processBtn.querySelector(".btn-text").classList.remove("hidden");
        processBtn.querySelector(".btn-loading").classList.add("hidden");
        processBtn.disabled = false;
    }

    function updateProgress(percent, text) {
        progressFill.style.width = percent + "%";
        progressText.textContent = text;
    }

    // --- Error ---

    function showError(message) {
        errorSection.classList.remove("hidden");
        errorMessage.textContent = message;
    }

    function hideError() {
        errorSection.classList.add("hidden");
    }

    // --- Utilities ---

    function formatFileSize(bytes) {
        if (bytes === 0) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
    }
});
