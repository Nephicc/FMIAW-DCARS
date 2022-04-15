

function func() {
    $.ajax({
        url: "display_rain/update",
        type:"GET",
        dataType: "json",
        success: function(data) {
            weather_data = JSON.parse(data);

            // console.log(data)
            console.log(weather_data)


            theChart.data.datasets = []

            let max = 0;
            let hours = [];
            for (const i in weather_data) {

                const ds = {
                    type: "line",
                    label: 'Station ' + weather_data[i]["station_id"],
                    data: weather_data[i]["rain"],
                    fill: false,
                    backgroundColor: weather_data[i]["color"],
                    borderColor: weather_data[i]["color"]
                };

                theChart.data.datasets.push(ds);

                if (weather_data[i]["hours"].length > max) {
                    max = weather_data[i]["hours"].length;
                    hours = weather_data[i]["hours"];
                }
            }

            theChart.data.labels = hours;

            theChart.update()
        }
    });
}


const ctx = document.getElementById("rain_temp_canvas");
var theChart = new Chart(ctx, {
    options: {
        scales: { y: { beginAtZero: true}
        },
        legend: { display: false },
        title: { display: true },
        animation: false
    }
});


setInterval(func,5000)

console.log(temp_data)
console.log(rain_data)
console.log(the_labels)