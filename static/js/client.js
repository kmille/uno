$(document).ready(function() {

(function worker() {
  $.ajax({
    url: '/games', 
    success: function(data) {
	 $("#games").empty();
	 $("#games").append(data);
    },
    complete: function() {
      setTimeout(worker, 2500);
    }
  });
})();

});
