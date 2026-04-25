const el = document.getElementById("chart-data");

const data = {
    Food: Number(el.dataset.food),
    Travel: Number(el.dataset.travel),
    Shopping: Number(el.dataset.shopping),
    Other: Number(el.dataset.other)
};

const ctx = document.getElementById("expenseChart").getContext("2d");

new Chart(ctx, {
    type: "pie",
    data: {
        labels: Object.keys(data),
        datasets: [{
            data: Object.values(data)
        }]
    }
});