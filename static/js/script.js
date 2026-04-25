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
            <div>
                <strong>${exp.name} - ₹${amount}</strong><br>
                <small style="color: gray;">${exp.category}</small>
            </div>
            <div>
                <button onclick="editExpense(${exp.id}, '${exp.name}', ${amount}, '${exp.category}')">✏️</button>
                <button class="delete-btn" onclick="deleteExpense(${exp.id})">❌</button>
            </div>
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

async function editExpense(id, oldName, oldAmount, oldCategory) {

    const name = prompt("Edit expense name:", oldName);
    if (name === null) return;

    const amount = prompt("Edit amount:", oldAmount);
    if (amount === null) return;

    const category = prompt("Edit category (Food/Travel/Shopping/Other):", oldCategory);
    if (category === null) return;

    await fetch(`/edit/${id}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            name: name,
            amount: parseInt(amount),
            category: category
        })
    });

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
                backgroundColor: [
                    "#4CAF50",
                    "#ff7e5f",
                    "#36A2EB",
                    "#999999"
                ]
            }]
        }
    });
}