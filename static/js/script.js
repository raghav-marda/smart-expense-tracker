const form = document.getElementById("expense-form");
const list = document.getElementById("expense-list");
const totalEl = document.getElementById("total");

let chart;

window.onload = loadExpenses;

// ADD EXPENSE
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

// LOAD EXPENSES
async function loadExpenses() {
    const res = await fetch("/get");
    const data = await res.json();

    list.innerHTML = "";
    let total = 0;

    let categoryData = {};

    data.forEach(exp => {
        const amount = parseInt(exp.amount);

        total += amount;

        // LIST ITEM FIXED
        const li = document.createElement("li");
        li.innerHTML = `
            <div>
                <strong>${exp.name}</strong> - ₹${amount}
                <br>
                <small>${exp.category}</small>
            </div>
            <button class="delete-btn" onclick="deleteExpense(${exp.id})">❌</button>
        `;

        list.appendChild(li);

        // CHART DATA FIX
        if (!categoryData[exp.category]) {
            categoryData[exp.category] = 0;
        }
        categoryData[exp.category] += amount;
    });

    totalEl.textContent = total;

    updateChart(categoryData);
}

// DELETE
async function deleteExpense(id) {
    await fetch(`/delete/${id}`, {method: "DELETE"});
    loadExpenses();
}

// CHART FIXED
function updateChart(data) {
    const ctx = document.getElementById("expenseChart");

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "pie",
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    "#4CAF50",
                    "#ff7e5f",
                    "#36A2EB",
                    "#FFCE56"
                ]
            }]
        }
    });
}