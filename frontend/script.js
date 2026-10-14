// Determine backend API URL (supports both same-host serving and Live Server on port 5500)
const API_URL = (window.location.protocol.startsWith("http") && window.location.port === "8000")
    ? window.location.origin
    : "http://127.0.0.1:8000";

// DOM Elements
const form = document.getElementById("certificateForm");
const recipientsContainer = document.getElementById("recipients");
const addRecipientBtn = document.getElementById("addRecipient");
const clearAllBtn = document.getElementById("clearAllBtn");
const generateBtn = document.getElementById("generateBtn");
const recipientCountBadge = document.getElementById("recipientCountBadge");
const statusMessage = document.getElementById("statusMessage");
const resultContainer = document.getElementById("result");

// Bulk Panel Elements
const toggleBulkBtn = document.getElementById("toggleBulkBtn");
const bulkPanel = document.getElementById("bulkPanel");
const bulkInput = document.getElementById("bulkInput");
const parseBulkBtn = document.getElementById("parseBulkBtn");
const closeBulkBtn = document.getElementById("closeBulkBtn");
const loadSampleBtn = document.getElementById("loadSampleBtn");

// Helper to create a recipient row
function createRecipientRow(name = "", email = "") {
    const row = document.createElement("div");
    row.className = "recipient-row";

    row.innerHTML = `
        <div class="input-wrapper name-col">
            <input
                type="text"
                name="name"
                placeholder="Recipient Full Name"
                value="${name.replace(/"/g, '&quot;')}"
                required
            >
        </div>

        <div class="input-wrapper email-col">
            <input
                type="email"
                name="email"
                placeholder="name@example.com"
                value="${email.replace(/"/g, '&quot;')}"
                required
            >
        </div>

        <div class="action-col">
            <button type="button" class="btn-icon removeRecipient" title="Remove recipient">
                ✕
            </button>
        </div>
    `;

    return row;
}

// Update row count badge and toggle remove button disabled state
function updateRecipientState() {
    const rows = recipientsContainer.querySelectorAll(".recipient-row");
    const count = rows.length;

    recipientCountBadge.textContent = `${count} Recipient${count === 1 ? "" : "s"}`;

    const removeButtons = recipientsContainer.querySelectorAll(".removeRecipient");
    removeButtons.forEach(btn => {
        btn.disabled = count <= 1;
    });
}

// Add a new row
addRecipientBtn.addEventListener("click", () => {
    const currentCount = recipientsContainer.querySelectorAll(".recipient-row").length;

    if (currentCount >= 100) {
        showStatus("Maximum limit of 100 recipients reached.", "error");
        return;
    }

    const row = createRecipientRow();
    recipientsContainer.appendChild(row);
    updateRecipientState();

    // Focus name input in the new row
    const nameInput = row.querySelector('[name="name"]');
    if (nameInput) nameInput.focus();
});

// Remove a row
recipientsContainer.addEventListener("click", (event) => {
    const removeBtn = event.target.closest(".removeRecipient");
    if (!removeBtn) return;

    const rows = recipientsContainer.querySelectorAll(".recipient-row");
    if (rows.length > 1) {
        removeBtn.closest(".recipient-row").remove();
        updateRecipientState();
    }
});

// Clear all rows back to 1
clearAllBtn.addEventListener("click", () => {
    if (confirm("Reset all recipients?")) {
        recipientsContainer.innerHTML = "";
        recipientsContainer.appendChild(createRecipientRow());
        updateRecipientState();
        hideStatus();
        resultContainer.classList.add("hidden");
    }
});

// Bulk CSV Toggle
toggleBulkBtn.addEventListener("click", () => {
    bulkPanel.classList.toggle("hidden");
    if (!bulkPanel.classList.contains("hidden")) {
        bulkInput.focus();
    }
});

closeBulkBtn.addEventListener("click", () => {
    bulkPanel.classList.add("hidden");
});

loadSampleBtn.addEventListener("click", () => {
    bulkInput.value = `Aarav Sharma, aarav.sharma@example.com
Diya Patel, diya.patel@example.com
Rohan Gupta, rohan.gupta@example.com
Ananya Singh, ananya.singh@example.com
Zaid Khan, zaid.khan@example.com`;
});

parseBulkBtn.addEventListener("click", () => {
    const text = bulkInput.value.trim();
    if (!text) {
        showStatus("Please paste some text in Name, Email format.", "error");
        return;
    }

    const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
    const parsed = [];

    for (const line of lines) {
        // Skip header if present
        if (/^name\s*,\s*email/i.test(line)) continue;

        const parts = line.split(/[,;\t]/).map(p => p.trim());
        if (parts.length >= 2) {
            const name = parts[0];
            const email = parts[1];
            if (name && email) {
                parsed.push({ name, email });
            }
        }
    }

    if (parsed.length === 0) {
        showStatus("No valid recipient lines found. Use format: Name, Email", "error");
        return;
    }

    // Check if adding exceeds 100
    const existing = recipientsContainer.querySelectorAll(".recipient-row");
    const isFirstRowEmpty = existing.length === 1 &&
        !existing[0].querySelector('[name="name"]').value.trim() &&
        !existing[0].querySelector('[name="email"]').value.trim();

    if (isFirstRowEmpty) {
        recipientsContainer.innerHTML = "";
    }

    let addedCount = 0;
    for (const item of parsed) {
        const count = recipientsContainer.querySelectorAll(".recipient-row").length;
        if (count >= 100) {
            showStatus(`Stopped at 100 recipients limit. Added ${addedCount} recipients.`, "error");
            break;
        }
        recipientsContainer.appendChild(createRecipientRow(item.name, item.email));
        addedCount++;
    }

    updateRecipientState();
    bulkInput.value = "";
    bulkPanel.classList.add("hidden");
    showStatus(`Successfully added ${addedCount} recipient${addedCount === 1 ? "" : "s"}!`, "loading");
    setTimeout(hideStatus, 3000);
});

// Show / Hide Status banner
function showStatus(message, type = "error") {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.classList.remove("hidden");
}

function hideStatus() {
    statusMessage.classList.add("hidden");
    statusMessage.textContent = "";
}

// Form Submission
form.addEventListener("submit", async function (event) {
    event.preventDefault();
    hideStatus();
    resultContainer.classList.add("hidden");

    const eventName = document.getElementById("eventName").value.trim();
    const rows = recipientsContainer.querySelectorAll(".recipient-row");

    const recipients = Array.from(rows).map(row => ({
        name: row.querySelector('[name="name"]').value.trim(),
        email: row.querySelector('[name="email"]').value.trim()
    }));

    // Local Validation
    if (!eventName) {
        showStatus("Please enter an event name.", "error");
        document.getElementById("eventName").focus();
        return;
    }

    if (recipients.length === 0) {
        showStatus("At least one recipient is required.", "error");
        return;
    }

    for (let i = 0; i < recipients.length; i++) {
        if (!recipients[i].name) {
            showStatus(`Recipient #${i + 1} is missing a name.`, "error");
            return;
        }
        if (!recipients[i].email) {
            showStatus(`Recipient #${i + 1} is missing an email address.`, "error");
            return;
        }
    }

    // Check duplicate emails locally
    const emailSet = new Set();
    for (const person of recipients) {
        const low = person.email.toLowerCase();
        if (emailSet.has(low)) {
            showStatus(`Duplicate email address found: ${person.email}`, "error");
            return;
        }
        emailSet.add(low);
    }

    // Set UI to loading state
    generateBtn.disabled = true;
    generateBtn.textContent = "Generating Certificates...";
    showStatus(`Generating ${recipients.length} certificate${recipients.length === 1 ? "" : "s"}... Please wait.`, "loading");

    try {
        const response = await fetch(`${API_URL}/api/certificates`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                event_name: eventName,
                recipients: recipients
            })
        });

        let data;
        try {
            data = await response.json();
        } catch {
            throw new Error(`Server returned status ${response.status} (${response.statusText})`);
        }

        if (!response.ok) {
            let errorMsg = "Certificate generation failed.";
            if (data && data.detail) {
                if (Array.isArray(data.detail)) {
                    errorMsg = data.detail
                        .map(err => (err.msg || "Invalid input").replace(/^Value error,\s*/i, ""))
                        .join(", ");
                } else if (typeof data.detail === "string") {
                    errorMsg = data.detail.replace(/^Value error,\s*/i, "");
                }
            }
            throw new Error(errorMsg);
        }

        // Render Results
        renderResults(data);
        hideStatus();

    } catch (error) {
        showStatus(`Error: ${error.message}`, "error");
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = "Generate Certificates";
    }
});

// Render Results View
function renderResults(data) {
    resultContainer.innerHTML = "";

    const certIds = data.certificates.map(c => c.certificate_id).join(",");
    const zipUrl = `${API_URL}/api/certificates/download-zip?ids=${encodeURIComponent(certIds)}`;

    const header = document.createElement("div");
    header.className = "results-header";
    header.innerHTML = `
        <div class="results-header-info">
            <h3>✓ ${data.total_recipients} Certificates Generated Successfully</h3>
            <p>Event: <strong>${escapeHtml(data.event_name)}</strong></p>
        </div>
        <a href="${zipUrl}" class="btn btn-zip">
            📦 Download All (${data.total_recipients}) as ZIP
        </a>
    `;

    const grid = document.createElement("div");
    grid.className = "certificates-grid";

    data.certificates.forEach(cert => {
        const card = document.createElement("div");
        card.className = "certificate-card";

        const downloadUrl = `${API_URL}/api/certificates/${encodeURIComponent(cert.certificate_id)}/download`;

        card.innerHTML = `
            <div class="cert-info">
                <div class="cert-name">${escapeHtml(cert.name)}</div>
                <span class="cert-id-tag">${escapeHtml(cert.certificate_id)}</span>
            </div>
            <a href="${downloadUrl}" target="_blank" rel="noopener noreferrer" class="btn-download-pdf">
                Download PDF
            </a>
        `;

        grid.appendChild(card);
    });

    resultContainer.append(header, grid);
    resultContainer.classList.remove("hidden");

    // Smooth scroll down to results
    resultContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Initial state
updateRecipientState();

