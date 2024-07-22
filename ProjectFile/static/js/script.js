//BLOCKS FORM RELOADING WARNING
if ( window.history.replaceState ) {
  window.history.replaceState( null, null, window.location.href );
}

//HOMEPAGE

function aAlert(){
  alert("Success, the file was uploaded and will be in processing soon");
}

function saveDate(){

  var fromValue = document.getElementById("from").value
  var toValue = document.getElementById("to").value

  document.getElementById("from").value = fromValue;
  document.getElementById("to").value = toValue;

  document.getElementById("fromHidden").value = fromValue;
  document.getElementById("toHidden").value = toValue; 

}

function refreshDate(){

  var fromValue = document.getElementById("from").value
  var toValue = document.getElementById("to").value

  document.getElementById("fromHidden").value = fromValue;
  document.getElementById("toHidden").value = toValue;

  document.getElementById('month').click();


}
window.onload = function() {
    document.getElementById('month').click();
};

document.addEventListener("DOMContentLoaded", function () {
  saveDate()

  const dateForm = document.getElementById("dateForm");

  dateForm.addEventListener("submit", function (event) {
      event.preventDefault();
      const fromDate = document.getElementById("from").value;
      const toDate = document.getElementById("to").value;

      fetch(`/fetch_data?from=${fromDate}&to=${toDate}`)
          .then(response => response.json())
          .then(data => {
              updateCharts(data);
          })
          .catch(error => console.error('Error:', error));
  });

  function updateCharts(data) {
      const expenseTrendData = data.expenseTrend;
      const pieChartData = data.pieChart;
      const costTrackData = data.CostTrack;

      // Update Expense Trend Chart
      const ctx = document.getElementById('myChart').getContext('2d');
      new Chart(ctx, {
          type: 'line',
          data: {
              labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
              datasets: [{
                  label: 'Monthly Expenses ($)',
                  data: expenseTrendData,
                  borderWidth: 1
              }]
          },
          options: {
              scales: {
                  x: {
                      ticks: {
                          autoSkip: false
                      }
                  }
              }
          }
      });

      // Update Pie Chart
      const ctx2 = document.getElementById('pieChart').getContext('2d');
      new Chart(ctx2, {
          type: 'pie',
          data: {
              labels: ['Mortgage payments', 'Utilities', 'Housekeeping', 'Maintenance', 'Transportation', 'Online', 'Property', 'Marketing', 'Misc'],
              datasets: [{
                  data: pieChartData,
                  borderWidth: 1,
                  backgroundColor: [
                      'rgba(0, 0, 255, 0.6)',
                      'rgba(0, 0, 139, 0.6)',
                      'rgba(70, 130, 180, 0.6)',
                      'rgba(100, 149, 237, 0.6)',
                      'rgba(135, 206, 250, 0.6)',
                      'rgba(173, 216, 230, 0.6)',
                      'rgba(30, 144, 255, 0.6)',
                      'rgba(65, 105, 225, 0.6)',
                      'rgba(0, 191, 255, 0.6)'
                  ],
                  borderColor: '#1a1c24',
                  hoverBackgroundColor: [
                      'rgba(0, 0, 255, 0.8)',
                      'rgba(0, 0, 139, 0.8)',
                      'rgba(70, 130, 180, 0.8)',
                      'rgba(100, 149, 237, 0.8)',
                      'rgba(135, 206, 250, 0.8)',
                      'rgba(173, 216, 230, 0.8)',
                      'rgba(30, 144, 255, 0.8)',
                      'rgba(65, 105, 225, 0.8)',
                      'rgba(0, 191, 255, 0.8)'
                  ]
              }]
          }
      });

      // Update Cost Track Chart
      const ctx3 = document.getElementById('trackCost').getContext('2d');
      new Chart(ctx3, {
          type: 'bar',
          data: {
              labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
              datasets: [{
                  label: 'Cost',
                  data: costTrackData,
                  borderWidth: 1
              }]
          },
          options: {
            scales: {
                x: {
                    ticks: {
                        autoSkip: false
                    }
                }
            }
        }
      });
  }
});


