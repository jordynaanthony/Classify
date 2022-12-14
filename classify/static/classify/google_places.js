// $.getScript( "https://maps.googleapis.com/maps/api/js?key=" + google_api_key + "&libraries=places") 
// .done(function( script, textStatus ) {
//     google.maps.event.addDomListener(window, "load", initAutocomplete())

// })


// let autocomplete_a;
// let autocomplete_b;

// function initAutocomplete() {

//   autocomplete_a = new google.maps.places.Autocomplete(
//    document.getElementById('id-google-address-a'),
//    {
//        types: ['address'],
//        componentRestrictions: {'country': ['uk']},
//    })
  
//   autocomplete_a.addListener('place_changed', function(){
//     onPlaceChanged('a')
//   });


//   autocomplete_b = new google.maps.places.Autocomplete(
//    document.getElementById('id-google-address-b'),
//    {
//        types: ['address'],
//        componentRestrictions: {'country': ['uk']},
//    })
  
//   autocomplete_b.addListener('place_changed', function(){
//     onPlaceChanged('b')
//   });

// }


// function onPlaceChanged (addy){

//     let auto
//     let el_id
//     let lat_id
//     let long_id

//     if ( addy === 'a'){
//         auto = autocomplete_a
//         el_id = 'id-google-address-a'
//         lat_id = 'id-lat-a'
//         long_id = 'id-long-a'
//     }
//     else{
//         auto = autocomplete_b
//         el_id = 'id-google-address-b'
//         lat_id = 'id-lat-b'
//         long_id = 'id-long-b'
//     }

//     var geocoder = new google.maps.Geocoder()
//     var address = document.getElementById(el_id).value

//     geocoder.geocode( { 'address': address}, function(results, status) {

//         if (status == google.maps.GeocoderStatus.OK) {
//             var latitude = results[0].geometry.location.lat();
//             var longitude = results[0].geometry.location.lng();

//             $('#' + lat_id).val(latitude) 
//             $('#' + long_id).val(longitude) 

//             CalcRoute()
//         } 
//     }); 
// }


function validateForm() {
    var valid = true;
    $('.geo').each(function () {
        if ($(this).val() === '') {
            valid = false;
            return false;
        }
    });
    return valid
}

// }
// this is the function that converts a given location to map coordinates and project to map
function PlaceToMap(course){

    // set the target_position's value be the name of the place the user wants to go
    var destination = document.getElementById("id-google-address-b"+course).name
    if(destination.includes('Mechanical') && destination.includes('Engr')){
        destination = 'Mechanical & Aerospace Engineering'
    }
    document.getElementById("target_position").value=destination+', Charlottesville'

    // geocoder.geocode( { 'address': destination}, function(results, status) {

    //     if (status == google.maps.GeocoderStatus.OK) {
    //         var latitude = results[0].geometry.location.lat();
    //         var longitude = results[0].geometry.location.lng();

    //         $('#' + lat_id).val(latitude) 
    //         $('#' + long_id).val(longitude) 


    //     } 
    // }); 

    if ( validateForm() == true){
        var params = {
            current_position: $('#current_position').val(),
            target_position: $('#target_position').val(),
        };
  
        var esc = encodeURIComponent;
        var query = Object.keys(params)
            .map(k => esc(k) + '=' + esc(params[k]))
            .join('&');
  
        url = '/map?' + query
        window.location.assign(url)
    }
    
}

function On_Click(course){
    document.getElementById("id-google-address-b"+course).style.color = "blue";
}

function Off_Click(course){
    document.getElementById("id-google-address-b"+course).style.color = "";
}