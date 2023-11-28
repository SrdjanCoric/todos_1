// $(function() {
//   $(document).on('submit', 'form.delete', function(event) {
//     event.preventDefault();
//     event.stopPropagation();

//     let ok = confirm("Are you sure? This cannot be undone!");
//     if (ok) {
//       let form = $(this);

//       $.ajax({
//         url: form.attr("action"),
//         method: form.attr("method"),
//         success: function(data) {
//           if (data.redirect_url) {
//             window.location.href = data.redirect_url
//           }
//         }
//       });
//     }
//   });
// });

$(function() {
  $("form.delete").on('submit', (event) => {
    event.preventDefault();
    event.stopPropagation();

    let ok = confirm("Are you sure? This cannot be undone!");
    if (ok) {
      let form = $(event.target);
      let listItem = form.closest("li");

      $.ajax({
        url: form.attr("action"),
        method: form.attr("method"),
        dataType: "json",
        success: (response) => {
          if (response.success) {
            listItem.remove();
          } else {
            alert("An error occurred. Please try again.")
          }
        }
      });
    }
  });
});