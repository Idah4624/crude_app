document.addEventListener("DOMContentLoaded", function () {

    const deleteButtons =
        document.querySelectorAll(".delete-button");

    deleteButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const confirmed = confirm(
                "Are you sure you want to delete this student?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });

});