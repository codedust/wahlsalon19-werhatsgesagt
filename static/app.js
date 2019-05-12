var current_question = {};
var nextCiteTimeout = null;

function nextCite(){
  if (nextCiteTimeout != null) {
    window.clearTimeout(nextCiteTimeout);
    nextCiteTimeout = null;
  }
  $('.partybutton').removeClass('correct');
  $('.partybutton').removeClass('wrong');
  $('.partybutton').removeClass('desaturate');
  $('blockquote').text('');

  $.getJSON("api/question", function( data ) {
    current_question = data;
    $('q').text(data.short);
  });
}
nextCite();

$('.partybutton').click(function(el){
  console.log(el);
  var party = $(el.delegateTarget).attr('data-party');
  if (party == current_question.party) {
    $('.partybutton[data-party="'+party+'"]').addClass('correct');
    $('.partybutton').addClass('desaturate');
    $('.partybutton[data-party="'+party+'"]').removeClass('desaturate');
    $('blockquote').html('<h3>' + current_question.headline + '</h3>' + current_question.long + '– <a target="_blank" href="' + current_question.url + '"><cite>' + current_question.programName + '</cite></a>');
    $('blockquote').html($('blockquote').html().replace(current_question.short_not_redacted, '<strong>' + current_question.short_not_redacted + '</strong>'));
  } else {
    $('.partybutton[data-party="'+party+'"]').addClass('wrong');
  }
});

$('#nextCiteBtn').click(function(){
  nextCite();
});
