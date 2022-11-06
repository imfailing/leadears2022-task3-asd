ymaps.ready(['Heatmap']).then(function init() {

    Date.prototype.addDays = function(days) {
            var date = new Date(this.valueOf());
            date.setDate(date.getDate() + days);
            return date;
        }
    document.getElementById('slider-range').onclick = function(){
        var tstart = new Date($("#slider-range").slider("values", 0) * 1000).toJSON().slice(0, 10)
        var tfinish = new Date($("#slider-range").slider("values", 1) * 1000).toJSON().slice(0, 10)
        var newurl = `/heatmap/getdata?tstart=${tstart}&tfinish=${tfinish}`
        console.log(newurl)
        heatmap.setMap(null)        
        $.ajax({
            url:newurl,
            dataType: 'json',
            success: onZonesLoad
        });
    };
    
    function updateHeatDataMap(val){   
        var tstart = new Date('2021-01-01').addDays($("#slider-range1").slider("value")-val).toISOString().slice(0,10) 
        var tfinish = new Date('2021-01-01').addDays($("#slider-range1").slider("value")+val).toISOString().slice(0,10) 
        var newurl = `/heatmap/getdata?tstart=${tstart}&tfinish=${tfinish}`
        console.log(newurl)
        heatmap.setMap(null)        
        $.ajax({
            url:newurl,
            dataType: 'json',
            success: onZonesLoad
        });

    };
     
    document.getElementById('slider-range1').onclick = function(){updateHeatDataMap(Math.round($('#meaning').val()/2))}
     
    var slider1Autoplay = false;
    $("#slider-1-autoplay").on("click", function() {
    var meaning = Math.round($('#meaning').val()/2)
    if (slider1Autoplay === false) {
     slider1Autoplay = true
     asd = setInterval(function(){
    updateHeatDataMap(meaning)
     }, 1000)
    }
    else {
    slider1Autoplay = false
     clearInterval(asd);
    } 
    

   });
    
    var inputSearch = new ymaps.control.SearchControl({
        options: {
            // Пусть элемент управления будет
            // в виде поисковой строки.
            size: 'large',
            // Включим возможность искать
            // не только топонимы, но и организации.
            provider: 'yandex#search'            
        }
    });

    
    var myMap = new ymaps.Map('map', {
        center: [55.733835, 37.588227],
        zoom: 11,
        controls: [inputSearch, 'typeSelector', 'fullscreenControl', 'zoomControl']
    }, {minZoom: 11,
        maxZoom: 22
    });

    function onZonesLoad(data){
    var obj = data;


    var data = [];
    for (var i = 0; i < obj.length; i++) {
         data.push([obj[i].geoData.coordinates[0], obj[i].geoData.coordinates[1]])
    }
    window.heatmap = new ymaps.Heatmap(data, {
        // Радиус влияния.
        radius: 15,
        // Нужно ли уменьшать пиксельный размер точек при уменьшении зума. False - не нужно.
        dissipating: false,
        // Прозрачность тепловой карты.
        opacity: 0.8,
        // Прозрачность у медианной по весу точки.
        intensityOfMidpoint: 0.2,
        // JSON описание градиента.
        gradient: {
            0.1: 'rgba(128, 255, 0, 0.7)',
            0.2: 'rgba(255, 255, 0, 0.8)',
            0.7: 'rgba(234, 72, 58, 0.9)',
            1.0: 'rgba(162, 36, 25, 1)'
        }
    });
    heatmap.setMap(myMap);
};    
    $.ajax({
        url: '/heatmap/getdata',
        dataType: 'json',
        success: onZonesLoad
    });
    
    
});