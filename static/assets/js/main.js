/* ==============================================
--------------- Virtuwell Main.js ------------ */
jQuery(document).ready(function () {
	"use strict";
	// Init our app
	if ( $('.sticky-header').length && $(window).width() >= 768 ) {
		var sticky = new Waypoint.Sticky({
			element: $('.sticky-header')[0],
			stuckClass: 'fixed',
			offset: 0
		});
	}


	// Affix
	$('.nav-faq').affix({
		offset: {
			top: function() {
				return (this.top = $('.nav-faq').offset().top - 135);
			},
			bottom: function () {
				return this.bottom = 673;
			}
		}
	});
});