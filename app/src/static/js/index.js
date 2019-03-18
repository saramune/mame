$(function() {
    // 自動リンク
    var exp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    $('.js-autolink').each(function(index, el) {
        $(el).html($(el).html().replace(exp, "<a href='$1'>$1</a>"));
    });

    $('#tweet').on('click', function(){
        $('#hidden_tags').val($('#tags').val());
        $('#tweet_form').submit();
    });
});