const form = document.getElementById("expense-form");
const list = document.getElementById("expense-list");
const totalEl = document.getElementById("total");
const monthFilter = document.getElementById("month-filter");

let pieChart;
let lineChart;

window.onload = () => {
    loadExpenses();
    loadMonthlyChart();
};

monthFilter.addEventListener("change", loadExpenses);

// ---------------- ADD ----------------
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
    loadMonthlyChart();
});

// ---------------- LOAD ----------------
async function loadExpenses() {
    let url = "/get";

    if (monthFilter.value) {
        url += `?month=${monthFilter.value}`;
    }

    const res = await fetch(url);
    const data = await res.json();

    list.innerHTML = "";
    let total = 0;
    let categoryData = {};

    data.forEach(exp => {
        const amount = parseInt(exp.amount);
        total += amount;

        const li = document.createElement("li");

        const safeName = exp.name.replace(/'/g, "\\'");
        const safeCategory = exp.category.replace(/'/g, "\\'");

        li.innerHTML = `
            <div>
                <strong>${exp.name} - ₹${amount}</strong><br>
                <small style="color: gray;">${exp.category}</small>
            </div>
            <div>
                <button onclick="editExpense(${exp.id}, '${safeName}', ${amount}, '${safeCategory}')">✏️</button>
                <button class="delete-btn" onclick="deleteExpense(${exp.id})">❌</button>
            </div>
        `;

        list.appendChild(li);

        categoryData[exp.category] = (categoryData[exp.category] || 0) + amount;
    });

    totalEl.textContent = total;
    updatePieChart(categoryData);
}

// ---------------- DELETE ----------------
async function deleteExpense(id) {
    await fetch(`/delete/${id}`, {method: "DELETE"});
    loadExpenses();
    loadMonthlyChart();
}

// ---------------- EDIT ----------------
function editExpense(id, oldName, oldAmount, oldCategory) {
    const newName = prompt("Edit name:", oldName);
    if (!newName) return;

    const newAmount = prompt("Edit amount:", oldAmount);
    if (!newAmount) return;

    const categories = ["Food", "Travel", "Shopping", "Other"];

    let newCategory = prompt("Category:", oldCategory);

    if (!categories.includes(newCategory)) {
        newCategory = oldCategory;
    }

    fetch(`/edit/${id}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            name: newName,
            amount: parseInt(newAmount),
            category: newCategory
        })
    }).then(() => {
        loadExpenses();
        loadMonthlyChart();
    });
}

// ---------------- PIE ----------------
function updatePieChart(data) {
    const ctx = document.getElementById("expenseChart");

    if (pieChart) pieChart.destroy();

    pieChart = new Chart(ctx, {
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
        },
        options: {
            plugins: {
                legend: {
                    position: "top"
                }
            }
        }
    });
}

// ---------------- LINE ----------------
async function loadMonthlyChart() {
    const res = await fetch("/monthly-summary");
    const data = await res.json();

    const monthNames = {
        "01":"Jan","02":"Feb","03":"Mar","04":"Apr",
        "05":"May","06":"Jun","07":"Jul","08":"Aug",
        "09":"Sep","10":"Oct","11":"Nov","12":"Dec"
    };

    const labels = Object.keys(data).map(m => monthNames[m]);
    const values = Object.values(data);

    const ctx = document.getElementById("monthlyChart");

    if (lineChart) lineChart.destroy();

    lineChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Monthly Spending",
                data: values,
                borderColor: "#4CAF50",
                backgroundColor: "rgba(76,175,80,0.2)",
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// ---------------- EXPORT ----------------
function exportData() {
    window.location.href = "/export";
}