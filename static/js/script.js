$(document).ready(function () {



    var $pointer = $('#scale-pointer');
    var $caption = $('#scale-caption');

    $('#prediction-form').submit(function (event) {
        event.preventDefault();

        var formData = {
            'temp': $('#temp').val(),
            'RH': $('#RH').val(),
            'wind': $('#wind').val()
        };

        $.ajax({
            type: 'POST',
            url: '/predict',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                var probabilityPct = response.probability[1] * 100;
                var accuracyPct = (response.accuracy * 100).toFixed(2);


                $pointer.css('left', probabilityPct + '%').addClass('active');
                $caption.text('Predicted fire probability: ' + probabilityPct.toFixed(2) + '%');

                var riskLevel = "Low";
                if (probabilityPct >= 20 && probabilityPct < 40) riskLevel = "Moderate";
                else if (probabilityPct >= 40 && probabilityPct < 60) riskLevel = "High";
                else if (probabilityPct >= 60 && probabilityPct < 80) riskLevel = "Very High";
                else if (probabilityPct >= 80) riskLevel = "Extreme";

                var verdictClass = probabilityPct >= 50 ? 'is-risk' : 'is-safe';
                var icon = probabilityPct >= 50 ? 'fa-exclamation-triangle' : 'fa-leaf';
                var title = riskLevel + ' Fire Risk';

                var html =
                    '<div class="result-verdict ' + verdictClass + '">' +
                    '<i class="fas ' + icon + '"></i>' +
                    '<div>' +
                    '<div class="verdict-title">' + title + '</div>' +
                    '<p class="verdict-detail">Probability ' + probabilityPct.toFixed(2) + '% &middot; Model accuracy ' + accuracyPct + '%</p>' +
                    '</div>' +
                    '</div>';

                $('#result').html(html);
            },
            error: function (error) {
                console.log(error);
                if (error.status === 401) {
                    var response = JSON.parse(error.responseText);
                    window.location.href = response.redirect;
                    return;
                }
                $('#result').html(
                    '<div class="result-verdict is-risk">' +
                    '<i class="fas fa-exclamation-triangle"></i>' +
                    '<div>' +
                    '<div class="verdict-title">Prediction failed</div>' +
                    '<p class="verdict-detail">Could not reach the prediction service. Try again.</p>' +
                    '</div>' +
                    '</div>'
                );
            }
        });
    });


    $('.spin-up').click(function () {
        var $input = $(this).closest('.number-wrapper').find('input');
        var val = parseFloat($input.val()) || 0;
        var max = $input.attr('max');
        var nextVal = val + 1;
        if (max !== undefined && nextVal > parseFloat(max)) {
            nextVal = parseFloat(max);
        }
        $input.val(nextVal);
    });

    $('.spin-down').click(function () {
        var $input = $(this).closest('.number-wrapper').find('input');
        var val = parseFloat($input.val()) || 0;
        var min = $input.attr('min');
        var nextVal = val - 1;
        if (min !== undefined && nextVal < parseFloat(min)) {
            nextVal = parseFloat(min);
        }
        $input.val(nextVal);
    });
});