async function fetchPausedItems() {
    const token = prompt("Introduce tu Access Token:");
    const userId = prompt("Introduce tu User ID:");

    const response = await fetch(`/paused-items?token=${token}&user_id=${userId}`);
    const data = await response.json();

    const dataDiv = document.getElementById("data");
    if (data.error) {
        dataDiv.innerHTML = `<p>Error: ${data.error}</p>`;
    } else {
        dataDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const button = document.createElement("button");
    button.textContent = "Ver Publicaciones Pausadas";
    button.onclick = fetchPausedItems;
    document.body.appendChild(button);
});
