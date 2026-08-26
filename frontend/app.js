const API_URL = "http://127.0.0.1:8000";


async function loadTransactions() {

    const response = await fetch(
        `${API_URL}/transactions`
    );

    const transactions = await response.json();

    const transactionList =
        document.getElementById("transactionList");

    transactionList.innerHTML = "";

    transactions.forEach(transaction => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${transaction.date}</td>
            <td>${transaction.description}</td>
            <td>${transaction.category}</td>
            <td>${transaction.type}</td>
            <td>₹${transaction.amount}</td>
            <td>
                <button onclick="deleteTransaction(${transaction.id})">
                    Delete
                </button>
            </td>
        `;

        transactionList.appendChild(row);
    });
}


async function loadAnalytics() {

    const response = await fetch(
        `${API_URL}/analytics`
    );

    const data = await response.json();

    document.getElementById("income").textContent =
        `₹${data.income}`;

    document.getElementById("expenses").textContent =
        `₹${data.expenses}`;

    document.getElementById("savings").textContent =
        `₹${data.savings}`;
}


document
    .getElementById("transactionForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const transaction = {

            amount: Number(
                document.getElementById("amount").value
            ),

            type:
                document.getElementById("type").value,

            category:
                document.getElementById("category").value,

            description:
                document.getElementById("description").value,

            date:
                document.getElementById("date").value
        };


        await fetch(
            `${API_URL}/transactions`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(transaction)
            }
        );


        document
            .getElementById("transactionForm")
            .reset();


        await loadTransactions();
        await loadAnalytics();
    });


async function deleteTransaction(id) {

    await fetch(
        `${API_URL}/transactions/${id}`,
        {
            method: "DELETE"
        }
    );

    await loadTransactions();
    await loadAnalytics();
}

function setTodayDate() {
    const today = new Date();

    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");

    const formattedDate = `${year}-${month}-${day}`;

    document.getElementById("date").value = formattedDate;
}

setTodayDate();
loadTransactions();
loadAnalytics();