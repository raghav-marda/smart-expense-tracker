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
        li.innerHTML = `
            ${exp.name} - ₹${amount} (${exp.category})
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
                data: Object.values(data)
            }]
        }
    });
}