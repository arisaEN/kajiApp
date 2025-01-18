//eatのモーダルウィンドウ
function showInputForm(year, month) {
    const modal = document.getElementById(`modal-input-form-${year}-${month}`);
    modal.style.display = 'block';
}

function showEditForm(year, month, id) {
    if (window.innerWidth <= 768) {
        const modal = document.getElementById(`modal-edit-form-${year}-${month}-${id}`);
        modal.style.display = 'block';
    } else {
        alert('大きい画面ではモーダルウィンドウを使用しません。');
    }
}

function toggleDetails(year, month) {
    const detailsDiv = document.getElementById(`details-${year}-${month}`);
    if (detailsDiv.style.display === 'none') {
        detailsDiv.style.display = 'block'; // 表示
    } else {
        detailsDiv.style.display = 'none'; // 非表示
    }
}





function showEditModal(type, index) {
    const modal = document.getElementById(type + '-modal-' + index);
    modal.style.display = 'block';
}

function closeModal(type, index) {
    const modal = document.getElementById(type + '-modal-' + index);
    modal.style.display = 'none';
}


//eat
function closeModal2 (year, month) {
    var modal = document.getElementById('modal-input-form-' + year + '-' + month);
    modal.style.display = 'none';
}

//life
function showEditModal(type, index) {
    const modal = document.getElementById(type + '-modal-' + index);
    modal.style.display = 'block';
}

