// Scroll to top
function scrollToTop(scrollDuration) {
const   scrollHeight = window.scrollY,
        scrollStep = Math.PI / ( scrollDuration / 15 ),
        cosParameter = scrollHeight / 2;
var     scrollCount = 0,
        scrollMargin,
        scrollInterval = setInterval( function() {
            if ( window.scrollY != 0 ) {
                scrollCount = scrollCount + 1;  
                scrollMargin = cosParameter - cosParameter * Math.cos( scrollCount * scrollStep );
                window.scrollTo( 0, ( scrollHeight - scrollMargin ) );
            } 
            else clearInterval(scrollInterval); 
        }, 15 );
};


// Mobile Navigation
window.onload = function() {
  var width = window.innerWidth
|| document.documentElement.clientWidth
|| document.body.clientWidth;
  if (width < 1000) {
    document.getElementsbyTagName("ul").style.display = "none";
    document.getElementsbyClassName("nav-menu").innerHTML += "Menu";
  }
  else {
    $('.nav-menu').show();
  }
};

function toggle_nav(id) {
	var v = document.getElementById(id);
	if (v.style.display== 'none') {
		v.style.display = 'show';
	}
	else {
		v.style.display = 'none';
	}
};