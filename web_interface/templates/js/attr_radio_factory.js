/* global d3 */

/////////////////////////////////////////////////////////
/////////////// The Radar Chart Function ////////////////
/////////////// Written by Nadieh Bremer ////////////////
////////////////// VisualCinnamon.com ///////////////////
/////////// Inspired by the code of alangrafu ///////////
/////////////////////////////////////////////////////////
	
function RadarChart(id, data, options) {
	var cfg = {
	 w: 600,				//Width of the circle
	 h: 600,				//Height of the circle
	 margin: {top: 20, right: 20, bottom: 20, left: 20}, //The margins of the SVG
	 levels: 3,				//How many levels or inner circles should there be drawn
	 maxValue: 0, 			//What is the value that the biggest circle will represent
	 labelFactor: 1.25, 	//How much farther than the radius of the outer circle should the labels be placed
	 wrapWidth: 60, 		//The number of pixels after which a label needs to be given a new line
	 opacityArea: 0.35, 	//The opacity of the area of the blob
	 dotRadius: 4, 			//The size of the colored circles of each blog
	 opacityCircles: 0.1, 	//The opacity of the circles of each blob
	 strokeWidth: 2, 		//The width of the stroke around each blob
	 roundStrokes: false,	//If true the area and stroke will follow a round path (cardinal-closed)
	 color: d3.scaleOrdinal(d3.schemeCategory10),	//Color function
         logperc: true,          //If true, plot a logarithmic function
         minValue: 1e-5
	};
	
	//Put all of the options into a variable called cfg
	if('undefined' !== typeof options){
	  for(var i in options){
		if('undefined' !== typeof options[i]){ cfg[i] = options[i]; }
	  }//for i
	}//if
        
        // Let's make the FIRST thing we do be to truncate the data if it doesn't conform.
        if(cfg.logperc) {
            data[0] = data[0].map(function(o) {return {axis: o.axis, value: Math.max(1e-5, o.value)};});
        }
	
	//If the supplied maxValue is smaller than the actual one, replace by the max in the data
	var maxValue = Math.max(cfg.maxValue, d3.max(data, function(i){return d3.max(i.map(function(o){return o.value;}));}));
	var minValue = cfg.minValue;
        // We want something to truncate the data to this minimum value.
        
	var allAxis = (data[0].map(function(i, j){return i.axis;})),	//Names of each axis
		total = allAxis.length,					//The number of different axes
		radius = Math.min(cfg.w/2, cfg.h/2), 	//Radius of the outermost circle
		Format = d3.format('.2%'),			 	//Percentage formatting
		angleSlice = Math.PI * 2 / total;		//The width in radians of each "slice"
	
	//Scale for the radius
        if (cfg.logperc) {
            var rScale = d3.scaleLog()
		.range([0, radius])
		.domain([minValue, maxValue]);
        }
        else {
            var rScale = d3.scaleLinear()
                    .range([0, radius])
                    .domain([0, maxValue]);
        }	
        
	/////////////////////////////////////////////////////////
	//////////// Create the container SVG and g /////////////
	/////////////////////////////////////////////////////////

	//Remove whatever chart with the same id/class was present before
	d3.select(id).select("svg").remove();
	
	//Initiate the radar chart SVG
	var svg = d3.select(id).append("svg")
			.attr("width",  cfg.w + cfg.margin.left + cfg.margin.right)
			.attr("height", cfg.h + cfg.margin.top + cfg.margin.bottom)
			.attr("class", "radar"+id);
	//Append a g element		
	var g = svg.append("g")
			.attr("transform", "translate(" + (cfg.w/2 + cfg.margin.left) + "," + (cfg.h/2 + cfg.margin.top) + ")");
	
	/////////////////////////////////////////////////////////
	////////// Glow filter for some extra pizzazz ///////////
	/////////////////////////////////////////////////////////
	
	//Filter for the outside glow
	var filter = g.append('defs').append('filter').attr('id','glow'),
		feGaussianBlur = filter.append('feGaussianBlur').attr('stdDeviation','2.5').attr('result','coloredBlur'),
		feMerge = filter.append('feMerge'),
		feMergeNode_1 = feMerge.append('feMergeNode').attr('in','coloredBlur'),
		feMergeNode_2 = feMerge.append('feMergeNode').attr('in','SourceGraphic');

	/////////////////////////////////////////////////////////
	/////////////// Draw the Circular grid //////////////////
	/////////////////////////////////////////////////////////
	
	//Wrapper for the grid & axes
	var axisGrid = g.append("g").attr("class", "axisWrapper");
	
	//Draw the background circles
	axisGrid.selectAll(".levels")
	   .data(d3.range(1,(cfg.levels+1)).reverse())
	   .enter()
		.append("circle")
		.attr("class", "gridCircle")
		.attr("r", function(d, i){return radius/cfg.levels*d;})
		.style("fill", "#CDCDCD")
		.style("stroke", "#CDCDCD")
		.style("fill-opacity", cfg.opacityCircles)
		.style("filter" , "url(#glow)");

	//Text indicating at what % each level is
	axisGrid.selectAll(".axisLabel")
	   .data(d3.range(1,(cfg.levels+1)).reverse())  //does this also need to change?
	   .enter().append("text")
	   .attr("class", "axisLabel")
	   .attr("x", 4)
	   .attr("y", function(d){return -d*radius/cfg.levels;})
	   .attr("dy", "0.4em")
	   .style("font-size", "10px")
	   .attr("fill", "#737373")
	   .text(function(d,i) { return (
               (cfg.logperc) ? Format(maxValue / Math.pow(10, (cfg.levels - d)) ) : Format(maxValue * d/cfg.levels)
               ); 
            });
           // Make this log scale

	/////////////////////////////////////////////////////////
	//////////////////// Draw the axes //////////////////////
	/////////////////////////////////////////////////////////
	
	//Create the straight lines radiating outward from the center
	var axis = axisGrid.selectAll(".axis")
		.data(allAxis)
		.enter()
		.append("g")
		.attr("class", "axis");
	//Append the lines
	axis.append("line")
		.attr("x1", 0)
		.attr("y1", 0)
		.attr("x2", function(d, i){ return rScale(maxValue*1.1) * Math.cos(angleSlice*i - Math.PI/2); })
		.attr("y2", function(d, i){ return rScale(maxValue*1.1) * Math.sin(angleSlice*i - Math.PI/2); })
		.attr("class", "line")
		.style("stroke", "white")
		.style("stroke-width", "2px");

	//Append the labels at each axis
	axis.append("text")
		.attr("class", "legend")
		.style("font-size", "11px")
		.attr("text-anchor", "middle")
		.attr("dy", "0.35em")
		.attr("x", function(d, i){ return rScale(maxValue * cfg.labelFactor) * Math.cos(angleSlice*i - Math.PI/2); })
		.attr("y", function(d, i){ return rScale(maxValue * cfg.labelFactor) * Math.sin(angleSlice*i - Math.PI/2); })
		.text(function(d){return d;})
		.call(wrap, cfg.wrapWidth);

	/////////////////////////////////////////////////////////
	///////////// Draw the radar chart blobs ////////////////
	/////////////////////////////////////////////////////////
	
	//The radial line function
	var radarLine = d3.lineRadial()
                .curve(d3.curveBasisClosed)
		.radius(function(d) { return rScale(d.value); })
		.angle(function(d,i) {	return i*angleSlice; });
		
	if(cfg.roundStrokes) {
		radarLine.curve(d3.curveCardinalClosed);
	}
				
	//Create a wrapper for the blobs	
	var blobWrapper = g.selectAll(".radarWrapper")
		.data(data)
		.enter().append("g")
		.attr("class", "radarWrapper");
			
	//Append the backgrounds	
	blobWrapper
		.append("path")
		.attr("class", "radarArea")
		.attr("d", function(d,i) { return radarLine(d); })
		.style("fill", function(d,i) { return cfg.color(i); })
		.style("fill-opacity", cfg.opacityArea)
		.on('mouseover', function (d,i){
			//Dim all blobs
			d3.selectAll(".radarArea")
				.transition().duration(200)
				.style("fill-opacity", 0.1); 
			//Bring back the hovered over blob
			d3.select(this)
				.transition().duration(200)
				.style("fill-opacity", 0.7);	
		})
		.on('mouseout', function(){
			//Bring back all blobs
			d3.selectAll(".radarArea")
				.transition().duration(200)
				.style("fill-opacity", cfg.opacityArea);
		});
		
	//Create the outlines	
	blobWrapper.append("path")
		.attr("class", "radarStroke")
		.attr("d", function(d,i) { return radarLine(d); })
		.style("stroke-width", cfg.strokeWidth + "px")
		.style("stroke", function(d,i) { return cfg.color(i); })
		.style("fill", "none")
		.style("filter" , "url(#glow)");		
	
	//Append the circles
	blobWrapper.selectAll(".radarCircle")
		.data(function(d,i) { return d; })
		.enter().append("circle")
		.attr("class", "radarCircle")
		.attr("r", cfg.dotRadius)
		.attr("cx", function(d,i){ return rScale(d.value) * Math.cos(angleSlice*i - Math.PI/2); })
		.attr("cy", function(d,i){ return rScale(d.value) * Math.sin(angleSlice*i - Math.PI/2); })
		.style("fill", function(d,i,j) { return cfg.color(j); })
		.style("fill-opacity", 0.8);

	/////////////////////////////////////////////////////////
	//////// Append invisible circles for tooltip ///////////
	/////////////////////////////////////////////////////////
	
	//Wrapper for the invisible circles on top
	var blobCircleWrapper = g.selectAll(".radarCircleWrapper")
		.data(data)
		.enter().append("g")
		.attr("class", "radarCircleWrapper");
		
	//Append a set of invisible circles on top for the mouseover pop-up
	blobCircleWrapper.selectAll(".radarInvisibleCircle")
		.data(function(d,i) { return d; })
		.enter().append("circle")
		.attr("class", "radarInvisibleCircle")
		.attr("r", cfg.dotRadius*1.5)
		.attr("cx", function(d,i){ return rScale(d.value) * Math.cos(angleSlice*i - Math.PI/2); })
		.attr("cy", function(d,i){ return rScale(d.value) * Math.sin(angleSlice*i - Math.PI/2); })
		.style("fill", "none")
		.style("pointer-events", "all")
		.on("mouseover", function(d,i) {
			newX =  parseFloat(d3.select(this).attr('cx')) - 10;
			newY =  parseFloat(d3.select(this).attr('cy')) - 10;
					
			tooltip
				.attr('x', newX)
				.attr('y', newY)
				.text(Format(d.value))
				.transition().duration(200)
				.style('opacity', 1);
		})
		.on("mouseout", function(){
			tooltip.transition().duration(200)
				.style("opacity", 0);
		});
		
	//Set up the small tooltip for when you hover over a circle
	var tooltip = g.append("text")
		.attr("class", "tooltip")
		.style("opacity", 0);
	
	/////////////////////////////////////////////////////////
	/////////////////// Helper Function /////////////////////
	/////////////////////////////////////////////////////////

	//Taken from http://bl.ocks.org/mbostock/7555321
	//Wraps SVG text	
	function wrap(text, width) {
	  text.each(function() {
		var text = d3.select(this),
			words = text.text().split(/\s+/).reverse(),
			word,
			line = [],
			lineNumber = 0,
			lineHeight = 1.4, // ems
			y = text.attr("y"),
			x = text.attr("x"),
			dy = parseFloat(text.attr("dy")),
			tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", dy + "em");
			
		while (word = words.pop()) {
		  line.push(word);
		  tspan.text(line.join(" "));
		  if (tspan.node().getComputedTextLength() > width) {
			line.pop();
			tspan.text(line.join(" "));
			line = [word];
			tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
		  }
		}
	  });
	}//wrap	
	
}//RadarChart

//current test output
/*
{"data": 
[
    [[1.13926462e-05, 8.68367079e-06, 8.26331132e-07, 1.59706397e-05,
      1.28094871e-06, 8.16249212e-06, 1.85813533e-05, 9.99226213e-01,
      3.42013223e-11, 1.31673750e-09, 6.57270949e-09, 1.21247490e-06,
      1.59436837e-03, 5.20634300e-11],  
     [3.30719538e-02, 1.91006126e-04, 2.54796177e-01, 3.85732704e-07, 
      5.32508068e-07, 5.23587980e-04, 1.03593586e-04, 8.00433372e-06, 
      1.22029756e-04, 3.83108500e-06, 3.03483461e-07, 6.09460659e-03], 
     [4.60445508e-02, 4.22135054e-05, 1.87077720e-04, 4.58464725e-04, 
      1.85622059e-06, 8.04826959e-06, 1.70212354e-06, 1.66630698e-03, 
      3.57059122e-04, 5.10020733e-01],
     [8.04108353e-08, 8.12432826e-01, 1.10851765e-01],
    [9.85803083e-03, 4.14875001e-01, 1.71420776e-04, 2.18738501e-06, 
     11.24368069e-06, 2.59835250e-03, 7.92833998e-06, 2.26111342e-06, 
      9.63576313e-04, 6.42023133e-06, 1.81576668e-03, 2.49828048e-07]]
],
 "labels":
[
 ['Domestic Shorthair', 'Brown', 'White', 'None', 'Harlequin']
]
}

//List of attrs:
[
 ['Abyssinian', 'Balinese', 'Bengal', 'British Longhair', 
  'British Shorthair', 'Domestic Longhair', 'Domestic Medium Hair', 'Domestic Shorthair',
  'Exotic Shorthair', 'Maine Coon', 'Oriental Shorthair', 'Persian',
  'Siamese', 'Sphinx'],
 ['Black', 'Blue', 'Brown', 'Buff',
  'Chocolate', 'Cream', 'Grey', 'Orange',
  'Red', 'Seal', 'Silver', 'White'],
 ['Black', 'Blue', 'Brown', 'Buff',
  'Cream', 'Grey', 'None', 'Orange',
  'Seal', 'White'],
 ['Cream',
  'None',
  'White'],
 ['Calico', 'Harlequin', 'Mackerel', 'Marble',
  'None', 'Point', 'Spotted', 'Ticked',
  'Torbie', 'Tortoiseshell', 'Tuxedo', 'Van']
]
*/

// Our update function should be fairly simple; 
// We just need to update the values of the data
// We don't need to scale the axes or anything.

var attrLabels = ['breed', 'primary color', 'secondary color', 
                  'tertiary color', 'color modifier'];

var breedsArr = ['Abyssinian', 'Balinese', 'Bengal', 'British Longhair', 
                 'British Shorthair', 'Domestic Longhair', 'Domestic Medium Hair', 'Domestic Shorthair',
                 'Exotic Shorthair', 'Maine Coon', 'Oriental Shorthair', 'Persian',
                 'Siamese', 'Sphinx'];
  
var primColorArr = ['Black', 'Blue', 'Brown', 'Buff',
                    'Chocolate', 'Cream', 'Grey', 'Orange',
                    'Red', 'Seal', 'Silver', 'White'];
  
var secColorArr = ['Black', 'Blue', 'Brown', 'Buff',
                   'Cream', 'Grey', 'None', 'Orange',
                   'Seal', 'White'];
  
var tertColorArr = ['Cream',
                    'None',
                    'White'];
                
var colorModArr = ['Calico', 'Harlequin', 'Mackerel', 'Marble',
                   'None', 'Point', 'Spotted', 'Ticked',
                   'Torbie', 'Tortoiseshell', 'Tuxedo', 'Van'];
               
function makeData(vect, category) {
    // Here, produce the expected value for 'data' in the RadarChart function
    /*
     * should look like:
     * data = [
                [//iPhone
                      {axis:"Battery Life",value:0.22},
                      {axis:"Brand",value:0.28},
                      {axis:"Contract Cost",value:0.29},
                      {axis:"Design And Quality",value:0.17},
                      {axis:"Have Internet Connectivity",value:0.22},
                      {axis:"Large Screen",value:0.02},
                      {axis:"Price Of Device",value:0.21},
                      {axis:"To Be A Smartphone",value:0.50}			
                ],[//Samsung
                      {axis:"Battery Life",value:0.27},
                      {axis:"Brand",value:0.16},
                      {axis:"Contract Cost",value:0.35},
                      {axis:"Design And Quality",value:0.13},
                      {axis:"Have Internet Connectivity",value:0.20},
                      {axis:"Large Screen",value:0.13},
                      {axis:"Price Of Device",value:0.35},
                      {axis:"To Be A Smartphone",value:0.38}
                ],[//Nokia Smartphone
                      {axis:"Battery Life",value:0.26},
                      {axis:"Brand",value:0.10},
                      {axis:"Contract Cost",value:0.30},
                      {axis:"Design And Quality",value:0.14},
                      {axis:"Have Internet Connectivity",value:0.22},
                      {axis:"Large Screen",value:0.04},
                      {axis:"Price Of Device",value:0.41},
                      {axis:"To Be A Smartphone",value:0.30}
                ]
              ];
     */
    var retData = [];
    var categ = [];
    switch(category.toLowerCase()) {
        case 'breed':
            categ = breedsArr;
            break;
        case 'primary color':
            categ = primColorArr;
            break;
        case 'secondary color':
            categ = secColorArr;
            break;
        case 'tertiary color':
            categ = tertColorArr;
            break;
        case 'color modifier':
            categ = colorModArr;
            break;
        default:
            categ = breedsArr;
    }
    
    var i;
    for (i = 0; i < categ.length; i++) {
        retData = retData.concat({axis: categ[i], value: vect[i]});
    }
    
    return [retData];
};
  
  
  function make_all_data(vects) {
      // Returns an array whose elements can be passed to
      // RadarChart as data.
      var results = [];
      var i;
      for (i = 0; i < attrLabels.length; i++) {
          results = results.concat([
              makeData(vects[i], attrLabels[i])
          ]);
      };
      
      return results;
  };
  