function showLoading() {
    // ローディングメッセージを表示する処理
    const loadingMessage = document.createElement('div');
    loadingMessage.innerText = 'ロード中...';
    loadingMessage.style.position = 'fixed';
    loadingMessage.style.top = '50%';
    loadingMessage.style.left = '50%';
    loadingMessage.style.transform = 'translate(-50%, -50%)';
    loadingMessage.style.color = 'white';
    loadingMessage.style.fontSize = '24px';
    document.body.appendChild(loadingMessage);
    
    // 1秒後にメッセージを削除（必要に応じて調整）
    setTimeout(() => {
        document.body.removeChild(loadingMessage);
    }, 1000);
}

//色反転
function toggleIconColor(element) {
    const icon = element.querySelector('i');
    icon.classList.toggle('text-warning'); // アイコンの色を反転
}


//メニュー
function toggleMenu() {
    const sidebar = document.getElementById('sidebarMenu');
    if (sidebar.classList.contains('d-none')) {
        sidebar.classList.remove('d-none');
    } else {
        sidebar.classList.add('d-none');
    }
}