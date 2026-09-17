const registerButton = document.getElementById("register-button");
const subscribeButton = document.getElementById("subscribe-button");
const installButton = document.getElementById("install-button");
const statusBox = document.getElementById("status");
const publicKeyBox = document.getElementById("public-key");

let registration = null;
let deferredInstallPrompt = null;

function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let index = 0; index < rawData.length; index += 1) {
    outputArray[index] = rawData.charCodeAt(index);
  }

  return outputArray;
}

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    statusBox.textContent = "이 브라우저는 서비스워커를 지원하지 않습니다.";
    return;
  }

  registration = await navigator.serviceWorker.register("/static/sw.js");
  statusBox.textContent = "서비스워커 등록이 완료되었습니다.";
}

async function subscribePush() {
  const publicKey = publicKeyBox.textContent.trim();
  if (!publicKey || publicKey === "설정되지 않음") {
    statusBox.textContent = "VAPID public key가 설정되지 않았습니다.";
    return;
  }

  if (!registration) {
    await registerServiceWorker();
  }

  const permission = await Notification.requestPermission();
  if (permission !== "granted") {
    statusBox.textContent = "알림 권한이 허용되지 않았습니다.";
    return;
  }

  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(publicKey),
  });

  const response = await fetch("/api/subscribe", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(subscription),
  });

  const result = await response.json();
  statusBox.textContent = `${result.message} 현재 구독 수: ${result.count}`;
}

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  deferredInstallPrompt = event;
  installButton.style.display = "inline-block";
  statusBox.textContent = "앱처럼 설치할 수 있습니다.";
});

installButton.addEventListener("click", async () => {
  if (!deferredInstallPrompt) {
    statusBox.textContent = "이 브라우저에서는 메뉴에서 홈 화면에 추가가 필요할 수 있습니다.";
    return;
  }

  deferredInstallPrompt.prompt();
  await deferredInstallPrompt.userChoice;
  deferredInstallPrompt = null;
  installButton.style.display = "none";
});

window.addEventListener("appinstalled", () => {
  installButton.style.display = "none";
  statusBox.textContent = "앱 설치가 완료되었습니다.";
});

registerButton.addEventListener("click", registerServiceWorker);
subscribeButton.addEventListener("click", subscribePush);
