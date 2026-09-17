const sendButton = document.getElementById("send-button");
const titleInput = document.getElementById("title");
const bodyInput = document.getElementById("body");
const urlInput = document.getElementById("url");
const resultBox = document.getElementById("result");

sendButton.addEventListener("click", async () => {
  const response = await fetch("/api/send", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title: titleInput.value,
      body: bodyInput.value,
      url: urlInput.value,
    }),
  });

  const result = await response.json();
  resultBox.textContent = JSON.stringify(result, null, 2);
});
