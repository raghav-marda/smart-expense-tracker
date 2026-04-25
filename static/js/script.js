const form = document.getElementById("expense-form");
const list = document.getElementById("expense-list");
const totalEl = document.getElementById("total");

let chart;

window.onload = loadExpenses;

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("expense-name").value;
    const amount = parseInt(document.getElementById("expense-amount").value);
    const category = document.getElementById("category").value;

    await fetch("/add", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name, amount, category})
    });

    form.reset();
    loadExpenses();
});

async function loadExpenses() {
    const res = await fetch("/get");
    const data = await res.json();

    list.innerHTML = "";
    let total = 0;
    let categoryData = {};

    data.forEach(exp => {
        const amount = parseInt(exp.amount);
        total += amount;

        const li = document.createElement("li");

        // ✅ FIXED UI (same as original)
        li.innerHTML = `
            <div>
                <strong>${exp.name} - ₹${amount}</strong><br>
                <small style="color: gray;">${exp.category}</small>
            </div>
            <button class="delete-btn" onclick="deleteExpense(${exp.id})">❌</button>
        `;

        list.appendChild(li);

        categoryData[exp.category] = (categoryData[exp.category] || 0) + amount;
    });

    totalEl.textContent = total;
    updateChart(categoryData);
}

async function deleteExpense(id) {
    await fetch(`/delete/${id}`, {method: "DELETE"});
    loadExpenses();
}

function updateChart(data) {
    const ctx = document.getElementById("expenseChart");

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "pie",
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                // ✅ FIXED COLORS (match original)
                backgroundColor: [
                    "#4CAF50",  // Food
                    "#ff7e5f",  // Shopping
                    "#36A2EB",  // Travel
                    "#999999"   // Other
                ]
            }]
        }
    });
}