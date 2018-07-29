var singletonControllers = angular.module('singletonControllers', []);

singletonControllers.controller("analysisCtrl", ['$scope', '$http', '$interval', function ($scope, $http, $interval) {

    $scope.init = function(distances, sampleIDs, samplesInfo)
    {
        $scope.distances = distances;
        $scope.sampleIDs = sampleIDs;
        $scope.samplesInfo = samplesInfo;
    };

    // tsne parameters
    $scope.tsneInfoDisplay = 'iteration: 0, cost:0';
    $scope.tsneLearningRate = 10;
    $scope.tsnePerplexity = 2;
    $scope.tsneMaxIteration = 50;

    // Unselected dot size
    $scope.unselectedSize = 3.5;

    // Toggle between lasso and dragging
    $scope.lasso = true;
    $scope.action = "Switch to dragging";

    // Lasso analysis variables
    $scope.data = [];
    $scope.tableData = [];
    $scope.lassoSelect = [];

    // Variable for determining what to display in template and when
    $scope.plotted = false;
    $scope.analysing = false;
    $scope.loading = false;

    // Variables for number of items listed in tables/visualisations
    $scope.geneList = 5;
    $scope.averageList = 10;
    $scope.heatList = 10;

    var intervalId = -1;	// for setInterval method used by tsne clustering

    var svg = d3.select("#mainSvg");

    // Other variables used by the controller
    var scatterPlot = new scatterplot.ScatterPlot({'svg':svg, 'showLabels':true, 'hideOverlappingLabels':true});

    // Initialise lasso variable and declare area of web page it will execute on
    var lasso = d3.lasso()
                    .area(scatterPlot.svg); // area where the lasso can be started

    // Initialise colours to be assigned to each group
    var colour = d3.scale.category10();

    // Initialise variables for t-sne
    var tsne;
    var initialiseData = function() {
        // data for scatterPlot
        var groupColour;
        for (var i=0; i<$scope.distances[0].length; i++) {
            // If group data is not given, make all data points the same colour
            groupColour = $scope.samplesInfo ? $scope.samplesInfo[$scope.sampleIDs[i]] : 'Unassigned';
            $scope.data.push({
                'name': $scope.sampleIDs[i],
                'group': groupColour,
                'x': 0,
                'y': 0,
                'colour': colour(groupColour)
            });
        }
    };

    // Main plot function
    $scope.plot = function()
    {
        $scope.clearData();
        $scope.plotted = true;

        initialiseData();

        tsne = new tsnejs.tSNE({epsilon: parseFloat($scope.tsneLearningRate),
                                perplexity: parseInt($scope.tsnePerplexity),
                                dim: $scope.data.length}); // create a tSNE instance
        tsne.initDataDist($scope.distances);

        $scope.executeTsne();
    };

    $scope.executeTsne = function() {
        // Repeat run at regular intervals (milliseconds).
        // Using angular's $interval wrapper means no need for $scope.$apply for $scope variables
        if (tsne.iter<$scope.tsneMaxIteration) {
            intervalId = $interval($scope.step, 10);
        }
    };

    // Iterate through t-sne algorithm until max interation or user calls stopTsne()
    $scope.step = function()
    {
        $scope.singleStep();
        if (tsne.iter>=$scope.tsneMaxIteration) {
            $scope.stopTsne();
        }
    };

    // Execute a single iteration in the t-sne algorithm
    $scope.singleStep = function()
    {
        var cost = tsne.step(); // do a few steps
        $scope.tsneInfoDisplay = "iteration: " + tsne.iter + ", cost: " + cost.toFixed(2);

        // Get current solution
        var Y = tsne.getSolution();

        // Update the plot
        for (var i=0; i<$scope.data.length; i++) {
            $scope.data[i]['x'] = Y[i][0];
            $scope.data[i]['y'] = Y[i][1];
        }

        // Draw the plot
        d3.timer(scatterPlot.draw($scope.data));
        scatterPlot.createLegend(colour);

        $scope.callLasso();
    };

    // Stops tsne clustering run
    $scope.stopTsne = function()
    {
        $interval.cancel(intervalId);
        //clearInterval(intervalId);

        $scope.callLasso();
    };

    // Initialise lasso functionality on scatterplot
    $scope.callLasso = function()
    {
        scatterPlot.svg.call(scatterPlot.zoom)
                    .on("mousedown.zoom", null); // disable dragging event handled by zoom when lassoing

        scatterPlot.svg.call(lasso
                    .items(scatterPlot.circle)
                    .on("start",lasso_start) // lasso start function
                    .on("draw",lasso_draw) // lasso draw function
                    .on("end",lasso_end));
    };

    // Turn dot labels on/off
    $scope.toggleLabels = function() {
        scatterPlot.showLabels = !scatterPlot.showLabels;
        scatterPlot.removeHighlightLabel();
    };

    // Reset all t-sne/lasso data
    $scope.clearData = function()
    {
        $scope.data = [];
        $scope.tableData = [];
        $scope.lassoSelect = [];
        $scope.averageData = [];
        $scope.analysing = false;
    };

    // Switch between drawing a lasso line and dragging the plot
    $scope.toggleLasso = function()
    {
        if($scope.lasso) {
            // Enable Drag - Disable Lasso
            $scope.action = "Switch to lasso";
            scatterPlot.svg.call(scatterPlot.zoom);
            scatterPlot.svg.call(lasso).on("mousedown.drag", null);
        } else {
            // Disable Drag - Enable Lasso
            $scope.action = "Switch to dragging";
            scatterPlot.svg.call(scatterPlot.zoom).on("mousedown.zoom", null);
            scatterPlot.svg.call(lasso);
        }
        $scope.lasso = !$scope.lasso;
    };



    // Lasso functions to execute while lassoing
    var lasso_start = function() {
      lasso.items()
        .style("fill",null) // clear all of the fills
        .classed({"not_possible":true,"selected":false}); // style as not possible
    };

    var lasso_draw = function() {
      // Style the possible dots
      lasso.items().filter(function(d) {return d.possible===true})
        .classed({"not_possible":false,"possible":true});

      // Style the not possible dot
      lasso.items().filter(function(d) {return d.possible===false})
        .classed({"not_possible":true,"possible":false});
    };

    var lasso_end = function() {

      // Reset the color of all dots
      lasso.items()
         .style("fill", function(d) { return d.colour; });

      // Style the selected dots
      var selected = lasso.items().filter(function(d) {return d.selected===true})
        .classed({"not_possible":false,"possible":false})
        .attr("r",7);

      // Reset the style of the not selected dots
      lasso.items().filter(function(d) {return d.selected===false})
        .classed({"not_possible":false,"possible":false})

      for (i=0; i<selected[0].length;i++) {
          $scope.lassoSelect.push(selected[0][i].id.split("_")[1]);
      }
      $scope.lassoSelect.sort();

    };

    $scope.clearLasso = function()
    {
        $scope.lassoSelect = [];
        lasso.items()
        .attr("r", $scope.unselectedSize) // reset size
    };

    // Send to server an array containing the names of the sample ids selected
    // A nested dictionary is returned that contains the gene expressions relevant to each sample selected
    $scope.lassoAnalysis = function()
    {
        // Check points have been selected before requesting server
        if($scope.lassoSelect != 0) {
            $scope.analysing = true;
            $scope.loading = true;

            $http({
                method: "POST",
                url: '/lasso',
                data: {
                    lassoData: JSON.stringify($scope.lassoSelect)
                }
            }).then(function (response) {
                $scope.tableData = response.data['matrix'];
                $scope.averageData = response.data['average'];
                $scope.loading = false;
                $scope.setHeatMap();
            }, function (response) { // Error handler
                alert("Unable to retrieve data.");
                $scope.loading = false;
            });
        }
    };


    $scope.exportGeneExpressions = function(dataset_name)
    {
        // Client Side Export
        var sampleIDs = (Object.keys($scope.tableData));

        // Create header row for csv file. Takes into account the row names by making first cell blank
        var header_row = [''].concat(sampleIDs);
        var line = header_row.join(",");

        var rows = [];
        rows.push("data:text/csv;charset=utf-8," + line);

        $scope.averageData.forEach(function(geneData) {
            var gene = geneData['gene']
            var new_line = [];
            new_line.push(gene);
            sampleIDs.forEach(function(sampleID) {
                new_line.push($scope.tableData[sampleID][gene])
            });
            rows.push(new_line)
        });
        var csvData = rows.join("\n");

        // Create link to file with specified file name and download
        var utcnow = new Date()
        var now = new Date(utcnow.getTime() - utcnow.getTimezoneOffset() * 60000);

        var filename = dataset_name.toLowerCase().replace(' ', '_');
        filename += "-" + now.toJSON().slice(0, 10);
        filename += "-lasso_analysis.csv";

        var encodedUri = encodeURI(csvData);

        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", filename);
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);


        // Server side file creation
        //$http({
        //    method: "POST",
        //    url: '/exportGeneExpressions',
        //    data: {
        //        matrix: $scope.tableData,
        //        average: $scope.averageData
        //    }
        //}).then(function(response) {
        //    alert("File created);
        //}, function(response) { // Error handler
        //    alert("Something went wrong");
        //});
    };

    $scope.setHeatMap = function() {
        var setData = function() {
            var heatData = [];
            for (var i= 0, k=0; i < $scope.lassoSelect.length; i++) {           // sample ids
                for (var j=0; j<$scope.heatList; j++, k++) {                                // gene expressions
                   heatData[k] = [i, j,
                       $scope.tableData[$scope.lassoSelect[i]][$scope.averageData[j]['gene']]];
                }
            }

            return heatData
        };

        $('#heatmap').highcharts({

            chart: {
                type: 'heatmap',
                inverted: true,
                width: 900,
            },

            title: {
                text:''
            },

            xAxis: {
                categories: $scope.lassoSelect
            },

            yAxis: {
                categories: $scope.averageData.slice(0, $scope.heatList).map(function(d) {return d.gene;})
            },

            colorAxis: {
                stops: [
                    [0, '#3060cf'],
                    [0.5, '#fffbbc'],
                    [0.9, '#c4463a']
                ],
                min: -5
            },

            // Message that appears when mouse scrolls over a cell in the heatmap
            tooltip: {
                formatter: function() {
                    return "<b>Sample ID: </b>" + this.series.xAxis.categories[this.point.x] + "<br>" +
                           "<b>Gene: </b>" + this.series.yAxis.categories[this.point.y] + "<br>" +
                           this.point.value
                }
            },

            // Declare data and the maximum number of cells needed
            series: [{
                turboThreshold: 100000, // If the number of cells needed exceeds this then the entire chart will be rendered in black
                borderWidth: 0,
                data: setData()
            }]

        });
    };


    $scope.downloadScatterplot = function(dataset_name)
    {
        // convert svg to canvas
        canvg('canvas', '<svg>'+$("#mainSvg").html()+'</svg>');

        // output as png
        var canvas = document.getElementById("canvas");
        var img = canvas.toDataURL("image/png");

        // create filename
        var utcnow = new Date()
        var now = new Date(utcnow.getTime() - utcnow.getTimezoneOffset() * 60000);

        var filename = dataset_name.toLowerCase().replace(' ', '_');
        filename += "-" + now.toJSON().slice(0, 10);
        filename += "-scatterplot.png";

        var link = document.createElement("a");
        link.setAttribute("href", img);
        link.setAttribute("download", filename);
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
}]);
