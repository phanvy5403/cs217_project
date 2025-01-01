document.addEventListener('DOMContentLoaded', () => {
    const isAdmin = document.body.getAttribute('data-role') === 'admin';

    // Fetch laws based on search parameters
    function fetchLaws(query = '', vehicle = '', penalty = '', page = 1, per_page = 2) {
        const url = `/search?query=${encodeURIComponent(query)}&vehicle=${encodeURIComponent(vehicle)}&penalty=${encodeURIComponent(penalty)}&page=${page}&per_page=${per_page}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                const tableBody = document.getElementById('lawTableBody');
                tableBody.innerHTML = '';
                if (data.laws.length === 0) {
                    tableBody.insertAdjacentHTML('beforeend', `<tr><td colspan="${isAdmin ? 7 : 6}" class="text-center">Không tìm thấy dữ liệu</td></tr>`);
                } else {
                    data.laws.forEach((law, index) => {
                        const formattedDate = law.NgayApDung
                            ? new Date(law.NgayApDung).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
                            : '-';
                        const row = `
                            <tr>
                                <td onclick="showLawDetails(${JSON.stringify(law).replace(/"/g, '&quot;')})">${index + 1}</td>
                                <td onclick="showLawDetails(${JSON.stringify(law).replace(/"/g, '&quot;')})">${law.LoiViPham || '-'}</td>
                                <td onclick="showLawDetails(${JSON.stringify(law).replace(/"/g, '&quot;')})">${law.ChiTietLoi || '-'}</td>
                                <td onclick="showLawDetails(${JSON.stringify(law).replace(/"/g, '&quot;')})">${law.TenPhuongTien || '-'}</td>
                                <td onclick="showLawDetails(${JSON.stringify(law).replace(/"/g, '&quot;')})">${law.HinhPhat || '-'}</td>
                                <td onclick="showLawDetails(${JSON.stringify(law).replace(/"/g, '&quot;')})">${formattedDate || '-'}</td>
                                ${isAdmin ? `<td>
                                    <button class="btn btn-warning btn-sm me-2" onclick="showEditLawModal(${JSON.stringify(law).replace(/"/g, '&quot;')})">Sửa</button>
                                    <button class="btn btn-danger btn-sm" onclick="deleteLaw(${law.ID})">Xóa</button>
                                </td>` : ''}
                            </tr>`;
                        tableBody.insertAdjacentHTML('beforeend', row);
                    });

                    // Update pagination
                    updatePagination(data.page, data.per_page, data.total_count);
                }
            })
            .catch(error => {
                console.error('Error fetching laws:', error);
                const tableBody = document.getElementById('lawTableBody');
                tableBody.innerHTML = `<tr><td colspan="${isAdmin ? 7 : 6}" class="text-center text-danger">Lỗi khi tải dữ liệu</td></tr>`;
            });
    }

    // Update pagination controls
    function updatePagination(page, per_page, total_count) {
        const pagination = document.getElementById('pagination');
        pagination.innerHTML = '';

        const totalPages = Math.ceil(total_count / per_page);

        for (let i = 1; i <= totalPages; i++) {
            const pageItem = document.createElement('li');
            pageItem.className = `page-item ${i === page ? 'active' : ''}`;
            pageItem.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            pageItem.addEventListener('click', (e) => {
                e.preventDefault();
                fetchLaws(
                    document.getElementById('searchQuery').value,
                    document.getElementById('searchVehicle').value,
                    document.getElementById('searchPenalty').value,
                    i,
                    per_page
                );
            });
            pagination.appendChild(pageItem);
        }
    }

    // Show law details in modal
    function showLawDetails(law) {
        const formattedDate = law.NgayApDung
            ? new Date(law.NgayApDung).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' })
            : '-';
        document.getElementById('modalLawNumber').innerText = law.DieuKhoan || '-';
        document.getElementById('modalViolationName').innerText = law.LoiViPham || '-';
        document.getElementById('modalViolationDescription').innerText = law.ChiTietLoi || '-';
        document.getElementById('modalVehicleTypeName').innerText = law.TenPhuongTien || '-';
        document.getElementById('modalPenaltyAmount').innerText = law.HinhPhat || '-';
        document.getElementById('modalEffectiveDate').innerText = formattedDate || '-';
        const modal = new bootstrap.Modal(document.getElementById('lawDetailsModal'));
        modal.show();
    }

    // Show edit law modal with existing data
    function showEditLawModal(law) {
        document.getElementById('editDieuKhoan').value = law.DieuKhoan || '';
        document.getElementById('editLoiViPham').value = law.LoiViPham || '';
        document.getElementById('editChiTietLoi').value = law.ChiTietLoi || '';
        document.getElementById('editPhuongTien').value = law.TenPhuongTien || 'Mô tô, gắn máy';
        document.getElementById('editHinhPhat').value = law.HinhPhat || '';
        document.getElementById('editNgayApDung').value = law.NgayApDung || '';

        // Store the law ID for later use
        document.getElementById('saveEditedLawButton').setAttribute('data-law-id', law.ID);
        console.log('Editing law ID:', law.ID);

        const modal = new bootstrap.Modal(document.getElementById('editLawModal'));
        modal.show();
    }

    // Delete law
    function deleteLaw(lawId) {
        if (confirm('Bạn có chắc chắn muốn xóa luật này?')) {
            fetch(`/delete/${lawId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => response.json())
                .then(result => {
                    if (result.message === 'Law deleted successfully!') {
                        alert('Xóa luật thành công!');
                        fetchLaws(); // Refresh law list
                    } else {
                        alert('Không thể xóa luật. Vui lòng thử lại.');
                    }
                })
                .catch(error => console.log('Error deleting law:', error));
        }
    }

    // Attach functions to the window object
    window.showLawDetails = showLawDetails;
    window.showEditLawModal = showEditLawModal;
    window.deleteLaw = deleteLaw;

    // Event listeners for dynamic search input
    const searchElements = ['searchQuery', 'searchVehicle', 'searchPenalty'];
    searchElements.forEach(id => {
        document.getElementById(id).addEventListener(id === 'searchVehicle' ? 'change' : 'input', () => {
            fetchLaws(
                document.getElementById('searchQuery').value,
                document.getElementById('searchVehicle').value,
                document.getElementById('searchPenalty').value
            );
        });
    });

    // Fetch laws when the page is loaded
    fetchLaws();

    // Save new law
    document.getElementById('saveLawButton').addEventListener('click', () => {
        const lawData = {
            DieuKhoan: document.getElementById('DieuKhoan').value,
            LoiViPham: document.getElementById('LoiViPham').value,
            ChiTietLoi: document.getElementById('ChiTietLoi').value,
            TenPhuongTien: document.getElementById('PhuongTien').value,
            HinhPhat: document.getElementById('HinhPhat').value,
            NgayApDung: document.getElementById('NgayApDung').value,
        };

        fetch('/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(lawData),
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('Thêm luật thành công!');
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addLawModal'));
                    modal.hide();
                    fetchLaws(); // Refresh law list
                } else {
                    alert('Không thể thêm luật. Vui lòng thử lại.');
                }
            })
            .catch(error => console.log('Error adding law:', error));
    });

    // Save edited law
    document.getElementById('saveEditedLawButton').addEventListener('click', () => {
        const lawId = document.getElementById('saveEditedLawButton').getAttribute('data-law-id');
        console.log('Saving edited law ID:', lawId);
        const lawData = {
            HinhPhat: document.getElementById('editHinhPhat').value,
            NgayApDung: document.getElementById('editNgayApDung').value,
        };

        fetch(`/update/${lawId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(lawData),
        })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(result => {
                console.log('Result:', result);
                if (result.message === 'Cập nhật luật thành công!') {
                    alert('Cập nhật luật thành công!');
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editLawModal'));
                    modal.hide();
                    fetchLaws(); // Refresh law list
                } else {
                    alert('Không thể cập nhật luật. Vui lòng thử lại.');
                }
            })
            .catch(error => {
                console.log('Error editing law:', error);
                alert(`Error editing law: ${error.message}`);
            });
    });
});
