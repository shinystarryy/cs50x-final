document.addEventListener('DOMContentLoaded', function () {
    const confirmDeleteModal = document.getElementById('confirmDeleteModal');
    const deleteForm = document.getElementById('deleteForm');

    if (confirmDeleteModal) {
        confirmDeleteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const taskId = button.getAttribute('data-task-id');
            deleteForm.action = `/delete_task/${taskId}`;
        });
    }

    const editTaskModal = document.getElementById('editTaskModal');
    if (editTaskModal) {
        editTaskModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;

            document.getElementById("edit-task-id").value = button.getAttribute("data-task-id");
            document.getElementById("edit-content").value = button.getAttribute("data-task-content");
            document.getElementById("edit-description").value = button.getAttribute("data-task-description") || "";
            document.getElementById("edit-priority").value = button.getAttribute("data-task-priority");
            document.getElementById("edit-due-date").value = button.getAttribute("data-task-due-date") || "";
        });
    }
});
