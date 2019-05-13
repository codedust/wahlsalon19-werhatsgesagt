var current_quote = {};
var nextCiteTimeout = null;

function nextCite(hash){
  if (nextCiteTimeout != null) {
    window.clearTimeout(nextCiteTimeout);
    nextCiteTimeout = null;
  }
  $('.partybutton').removeClass('correct');
  $('.partybutton').removeClass('wrong');
  $('.partybutton').removeClass('desaturate');
  $('.correctBanner').hide();
  $('blockquote').hide();

  var request_url = 'api/quote';
  try {
    params = atob(hash.substr(1)).split(',');
    if (params.length == 3) {
      request_url = 'api/quote/' + encodeURI(params[2]) + '/' + parseInt(params[0]) + '/' + parseInt(params[1]);
    }
  } catch(e) {
    request_url = 'api/quote';
  }

  $.getJSON(request_url, function( data ) {
    current_quote = data;
    $('q').text(data.short);
    location.hash = btoa(data.line_number + ',' + data.sentence_number + ',' + data.party);
    var url = location.href;
    var text = "Aus welchem Wahlprogramm stammt dieses Zitat? #Wahlprogrammquiz #Europawahl2019\n\n";
    var maxDataShortLength = 279-text.length-url.length-2;
    var quote = (data.short.length > maxDataShortLength ? data.short.substr(0, maxDataShortLength-3) + "..." : data.short);
    $('.twitterBtn').attr("href", "https://twitter.com/intent/tweet?url=" + encodeURIComponent(url) + "&text=" + encodeURIComponent(text) + encodeURIComponent("„" + quote + "“"));
    scrollIntoViewIfNeeded(document.getElementById('quotesection'));
  });
}
nextCite(location.hash);

window.onhashchange = function() {
  nextCite(location.hash);
};

$('.partybutton').click(function(el){
  var party = $(el.delegateTarget).attr('data-party');
  if (party == current_quote.party) {
    $('.partybutton[data-party="'+party+'"]').addClass('correct');
    $('.partybutton').addClass('desaturate');
    $('.partybutton[data-party="'+party+'"]').removeClass('desaturate');

    $('.correctBanner span').text(current_quote.programName.replace(' zur Europawahl 2019', ''));
    $('.correctBanner').show();

    $('blockquote').html('<h3>' + current_quote.headline + '</h3>' + current_quote.long + '– <a target="_blank" href="' + current_quote.url + '"><cite>' + current_quote.programName + '</cite></a>');
    $('blockquote').html($('blockquote').html().replace(current_quote.short_not_redacted, '<strong>' + current_quote.short_not_redacted + '</strong>'));
    $('blockquote').show();

    window.setTimeout(function(){
      scrollIntoViewIfNeeded(document.getElementsByClassName('correctBannerScrollAnchor')[0]);
    }, 50); // wait until DOM update is done
  } else {
    $('.partybutton[data-party="'+party+'"]').addClass('wrong');
  }
});

function scrollIntoViewIfNeeded(target) {
  var rect = target.getBoundingClientRect();
  if (rect.bottom > window.innerHeight || rect.top < 0) {
    target.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
  }
}

$('#nextCiteBtn').click(function(){
  nextCite();
});
