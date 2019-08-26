/* jQuery AnimateCSS Extention*/

$.fn.extend({
    animateE: function(animation, callback) {
        var animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
        this.addClass('animated ' + animation).one(animationEnd, function() {
            $(this).removeClass('animated ' + animation);
            if(callback) {
                callback();
            }
        });
        return this;
    }
});

var searchKW = "", showResults = false, status = 0, pagination = 1;

function getArticles() {
    var results = "";
    $.ajax({
        url: 'https://en.wikipedia.org/w/api.php?action=opensearch&search='+searchKW+'&format=json&limit='+pagination+'0&callback=wikicallback',
        dataType: 'jsonp',
    }).done(function(data) {
        var titles = data[1], excerpts = data[2], links = data[3];
        titles.forEach(function(e,i,a) {
            results += $("#templateA").html().replace(/{link}/, links[i])
            .replace(/{title}/, e).replace(/{excerpt}/, excerpts[i]);
            if(i == a.length-1) {
                results += '<div><a href="#" id="load-more"><i class="fa fa-refresh" aria-hidden="true"></i> Load More</a></div>'
            }
            status = 1;
        });
    }).fail(function(error) {
        results += "<div class=\"error\">An error occurred, please try again later...</div>"
        status = 0;
    }).always(function() {
        showResults = true;
        $("#articles").append(results);
        articles(true);
    });
}

function articles(show) {
    if(show && showResults) {
        $(".container").removeClass("search-mode");
        $("#articles").fadeIn();
        if(status) loadMore();
    } else {
        searchKW = ""; showResults = false; status = 0; pagination = 1;
        $("#results").fadeOut(300, function() {
            $("#articles").html("").css("display", "none");
            $(".container").addClass("search-mode");
            $("#search-box").val("");
            searchForm(true);
        });
    }
}

function moreArticles() {
    $("#articles").fadeOut(300).html("");
    pagination++;
    getArticles();
}

function searchForm(show) {
    if(show) {
        $("#search").css("display", "block");
        $("#search .title").css("opacity", 1).animateE("fadeInDown", function() {
            $("#search-form").css("opacity", 1).animateE("fadeIn", function() {
                $(".random-article").css("opacity", 1).animateE("fadeIn");
            });
        });
    } else {
        $(".random-article").animateE("fadeOut", function() {
            $("#search-form").animateE("fadeOut", function() {
                $("#search .title").animateE("fadeOutUp", function(e) {
                    $("#search .title").css("opacity", 0);
                    $("#search").css("display", "none");
                });
            }).css("opacity", 0);
        }).css("opacity", 0);
    }
}

$("#close-icon").on("click", function(event) {
    articles(false);
    event.preventDefault();
});

$("#search-form").on("submit", function(event) {
    if($("#search-box").val().length <= 0) return;
    searchKW = $("#search-box").val();

    searchForm(false);

    setTimeout(function() {
        $("#results").animateE("fadeIn").css("display", "block");
        getArticles();
    }, 1700);

    event.preventDefault();
});

function loadMore() {
    $("#load-more").on("click", function(event) {
        moreArticles();
        event.preventDefault();
    });
}


$(window).on("scroll", function() {
    if($(this).scrollTop() >= 40) {
        $(".header").addClass("dark");
    } else {
        $(".header").removeClass("dark");
    }
})

$(document).ready(function() {
    $("#search").css("display", "block");
    searchForm(true);
});