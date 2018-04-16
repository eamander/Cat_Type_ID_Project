var image_zone;
var image_upload_button;
var image_link_zone;
var test_var;
var img;
var img_data;
//function setup(){
////    special p5 func that is called to setup the page
//  
//    image_zone = select('#disp_img');  // The image element
//    image_upload_button = select('#image_upload_button');
//    image_link_zone = select('#img_url_input');
//    
//    image_zone.drop(gotFile);
//    image_upload_button.drop(gotFile);
//    image_link_zone.drop(gotFile);
//
//    // image_zone:
////    do any pre-processing to
//};
//
//// In getImage, get the image, then send it.
//
//function gotFile(file){
//    // Start by naing it just load at the right place
//    test_var = file;
//    // OK so get image data, find the source, use that.
//    createP(file.name + " " + file.size);
//    var img = createImg(file.data);
//}




// new construction
var sketch = function(p){
//    var img;
//    p.preload = function(){
////        var img;
//        img = p.loadImage("images/dmh_277.jpg");
//        img.addClass("img-responsive center-block imground");
//    };
    
    
    p.setup = function(){
    //    special p5 func that is called to setup the page

//        image_zone = p.select('#disp_img');  // The image element
        image_upload_button = p.select('#image_upload_button');
        image_link_zone = p.select('#img_url_input');

//        image_zone.drop(gotFile);
        image_upload_button.drop(gotFile);
        image_link_zone.drop(gotFile);

        // image_zone:
    //    do any pre-processing to
        img = p.createImg("images/dmh_277.jpg");
        img.addClass("img-responsive center-block imground");
        img.attribute('id', 'disp_img');
        image_zone = p.select('#disp_img');
        image_zone.drop(gotFile);
};

    function gotFile(file){
        // Start by naing it just load at the right place
//        p.removeElements();
        var elem = document.getElementById("disp_img");
        elem.parentNode.removeChild(elem);
        
        test_var = file;
        // OK so get image data, find the source, use that.
        img = p.createImg(file.data);
        img.addClass("img-responsive center-block imground");
        img.attribute('id', 'disp_img');
        image_zone = p.select('#disp_img');
        image_zone.drop(gotFile);
        img_data = p.loadImage(file.data);
        img_data.loadPixels();
        // access pixels by: img_Data.pixels
        // try sending this array
        // can also try sending string repr and parsing
};
};

// reference: <!--<img id="disp_img" src="images/dmh_277.jpg" alt="Cat Image Goes Here" class="img-responsive center-block imground">-->
new p5(sketch, window.document.getElementById('disp_img_border'));