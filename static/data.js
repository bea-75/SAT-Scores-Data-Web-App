$(document).ready(function() {
    $(".state").hide();
    $(".year").hide();
    
	$(".overtime").click(function() {
		$(".state").show();
        $(".year").hide();
	});
    $(".range").click(function() {
		$(".state").show();
        $(".year").show();
	});
    $(".country").click(function() {
		$(".year").show();
        $(".state").hide();
	});
    
});