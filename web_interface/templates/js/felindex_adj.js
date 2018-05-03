var image_zone;
var image_upload_button;
var image_link_zone;
var img_file;
var img;
var img_data;
var testCheck1;
var testCheck2;
var testCheck3;



// new construction
var sketch = function(p){
  
    p.setup = function(){
    //    special p5 func that is called to setup the page

//        image_zone = p.select('#disp_img');  // The image element
        image_upload_button = p.select('#image_upload_button');
//        image_link_zone = p.select('#img_url_input');
        image_border = p.select('#disp_img_border');

//        image_zone.drop(gotFile);
        image_upload_button.drop(gotFile);
//        image_link_zone.drop(gotFile);
        image_border.drop(gotFile);

        // image_zone:
    //    do any pre-processing to
        img = p.createImg("images/dmh_277.jpg");
        img.addClass("img-responsive center-block imground");
        img.attribute('id', 'disp_img');
        image_zone = p.select('#disp_img');
        image_zone.drop(gotFile);
};

    function gotFile(file){
//        p.removeElements();
        var elem = document.getElementById("disp_img");
        elem.parentNode.removeChild(elem);
        
        img_file = file;
        // OK so get image data, find the source, use that.
        img = p.createImg(file.data);
        img.addClass("img-responsive center-block imground");
        img.attribute('id', 'disp_img');
        image_zone = p.select('#disp_img');
        image_zone.drop(gotFile);
        
        // access pixels by: img_Data.pixels
        // try sending this array
        // can also try sending string repr and parsing
    
        function loadPixCallback(the_img){
            // the_img.loadPixels();
            // Here, send the file data to the algorithm
            var input = {data: img_file.data};
            client.algo('algo://eamander/Felindex/')
                  .pipe(JSON.stringify(input))
                  .then(function(output) {
                      testCheck1 = output;
                      output = JSON.parse(output.result);
                      radarInputData = make_all_data(output.data[0]); 
                      testCheck2 = radarInputData;
                      imageLabels = output.labels[0];
                      testCheck3 = imageLabels;
                      // Then redraw the plots
                      drawCharts(radarInputData);
                      // Then change the labels:
                      changeLabels(imageLabels);
                  });
            // Re-write the function to work with SocketIO
//            socket.emit("algo", JSON.stringify(input), function(output) {
////                    testCheck1 = JSON.parse(output);
////                    radarInputData = make_all_data(output.data[0]);
////                    testCheck2 = radarInputData;
////                    imageLabels = output.labels[0];
////                    testCheck3 = imageLabels;
////                    drawCharts(radarInputData);
////                    changeLabels(imageLabels);
//                    // Before getting in to this, I just want to know that
//                    // I can get a proper response.
//                    console.log(output);
//                }
//            );
        };
        
        img_data = p.loadImage(file.data, loadPixCallback);
    };
};

// reference: <!--<img id="disp_img" src="images/dmh_277.jpg" alt="Cat Image Goes Here" class="img-responsive center-block imground">-->
new p5(sketch, window.document.getElementById('disp_img_border'));