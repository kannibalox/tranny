//@ sourceMappingURL=tranny.map
// Generated by CoffeeScript 1.6.1
(function() {
  var init, label_formatter, parse_json, render_pie_chart, render_rankings, render_section_totals;

  label_formatter = function(label, series) {
    var pct;
    pct = Math.round(series.percent);
    return "<div class=\"pie_label\">" + label + "<br/>" + pct + "% (" + series.data[0][1] + ")</div>";
  };

  parse_json = function(json_string) {
    return JSON && JSON.parse(json_string || jQuery.parseJSON(json_string));
  };

  /*
      Render a pie chart
  */


  render_pie_chart = function(dataset, element_id) {
    var options;
    options = {
      series: {
        pie: {
          show: true,
          radius: 1,
          label: {
            show: true,
            radius: 0.65,
            formatter: label_formatter,
            background: {
              opacity: 0
            }
          }
        }
      },
      legend: {
        show: true
      }
    };
    return jQuery.plot(element_id, dataset, options);
  };

  /*
      Fetch source totals and render in a pie graph
  */


  render_rankings = function() {
    return jQuery.get("/webui/stats/source_leaders", function(response) {
      var dataset;
      dataset = parse_json(response);
      return render_pie_chart(dataset, "#leader_board");
    });
  };

  render_section_totals = function() {
    return jQuery.get("/webui/stats/section_totals", function(response) {
      var dataset;
      dataset = parse_json(response);
      return render_pie_chart(dataset, "#section_totals");
    });
  };

  init = function() {
    render_rankings();
    return render_section_totals();
  };

  this.Tranny = {
    render_rankings: render_rankings
  };

  jQuery(function() {
    init();
    return console.log("started!");
  });

}).call(this);
