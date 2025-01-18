//main画面の登録チェック
function validateForm() {
    // フォームのすべての入力フィールドとセレクトフィールドを取得
    const inputs = document.querySelectorAll('input:not([type="submit"])');
    const selects = document.querySelectorAll('select');
    
    // 入力フィールドがすべて入力されているか確認
    for (let input of inputs) {
        if (input.value === '') {
            alert('すべてのフィールドを入力してください');
            return false; // フォームの送信をキャンセル
        }
    }

    // セレクトフィールドがすべて選択されているか確認
    for (let select of selects) {
        if (select.value === '') {
            alert('すべてのフィールドを入力してください');
            return false; // フォームの送信をキャンセル
        }
    }

    return true; // すべてのフィールドが入力されている場合、フォームを送信
}




//管理者画面へのパスワードチェック
function checkAdminPassword() {
    const password = prompt("パスワードを入力してください:");
    if (password === "admin") { // ここに正しいパスワードを設定
        return true; // パスワードが正しい場合、管理者画面へ進む
    } else {
        alert("パスワードが違います。"); // パスワードが間違っていた場合、警告を表示
        return false; // リンクの遷移をキャンセル
    }
}



//登録確認
function confirmSubmission() {
    const workSelect = document.getElementById('workSelect');
    const selectedOption = workSelect.options[workSelect.selectedIndex];
    document.getElementById('workId').value = selectedOption.value;
    document.getElementById('workName').value = selectedOption.text;

    if (!confirm("登録しますか？")) {
        return false;  // "いいえ"を選択した場合、フォーム送信を中止
    }
    document.forms[1].submit();  // "はい"を選択した場合のみフォームを送信
}

document.addEventListener('DOMContentLoaded', function() {
    var dateInput = document.getElementById('dateInput');
    var today = new Date();
    var day = ("0" + today.getDate()).slice(-2);
    var month = ("0" + (today.getMonth() + 1)).slice(-2);
    var todayString = today.getFullYear() + '-' + month + '-' + day;
    dateInput.value = todayString;
});





//登録空白チェック
function confirmRegistration(...fields) {
    for (let field of fields) {
        if (document.querySelector(`input[name="${field}"]`).value.trim() === '') {
            alert('テキストボックスが空です。登録をキャンセルします。');
            return false; // 登録をキャンセル
        }
    }
    return confirm('本当に登録しますか？'); // 確認ダイアログ
}





// function closeModal(year, month, id = null) {
//     if (id) {
//         const modal = document.getElementById(`modal-edit-form-${year}-${month}-${id}`);
//         modal.style.display = 'none';
//     } else {
//         const modal = document.getElementById(`modal-input-form-${year}-${month}`);
//         modal.style.display = 'none';
//     }
// }