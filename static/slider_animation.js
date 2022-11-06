$(function() {

  var format = "yy.mm.dd";
  var minDate = "2021.01.01";
  var maxDate = "2022.01.01";

  function formatDate(str) {
    var yy = str.slice(0, 4);
    var mm = str.slice(5, 7);
    var dd = str.slice(8);
    var f = yy + "-" + mm + "-" + dd;
    console.log("Format:", f);
    return f;
  }

  function strToDate(f, str) {
    return $.datepicker.parseDate(f, str);
  }

  function dateToStr(f, dt) {
    return $.datepicker.formatDate(f, dt);
  }

  function calcDayDiff(a, b) {
    var d1 = Date.parse(formatDate(a)),
      d2 = Date.parse(formatDate(b)),
      tdf = Math.abs(d2 - d1),
      ddf = Math.ceil(tdf / (1000 * 3600 * 24));
    console.log("Calc:", a, b, d1, d2, tdf, ddf);
    return ddf;
  }

  function addDays(dt, d) {
    var nt = d * (1000 * 3600 * 24);
    var ndt = new Date(dt.getTime() + nt);
    console.log("Add:", dt, d, nt, ndt);
    return ndt;
  }

  function dateToSeconds(dStr) {
    var dt = new Date(dStr);
    return dt.getTime() / 1000;
  }

  $("#slider-range1").slider({
    min: 0,
    max: calcDayDiff(minDate, maxDate),
    step: 1,
    value: calcDayDiff(minDate, "2021.01.01"),
    slide: function(event, ui) {
      var dtv = addDays(strToDate(format, minDate), ui.value);
      $("#date-slider-1").val(dtv.toLocaleString('ru', {
              year: 'numeric', month: 'long', day: 'numeric'}));
    }
  });

  var sdtv = addDays(strToDate(format, "2021.01.01"), $("#slider-range1").slider("value"));
  $("#date-slider-1").val(sdtv.toLocaleString('ru', {
          year: 'numeric', month: 'long', day: 'numeric'}));

  var slider1Autoplay = false;
  var intv = false;
  console.log("Init: ", slider1Autoplay, $("#slider-range1").slider("value"));

  $("#slider-1-autoplay").on("click", function() {
    var meaning = Number($('#meaning').val())
    var tmstp = Number($('#tmstp').val())
    slider1Autoplay = (slider1Autoplay) ? false : true;

    if (slider1Autoplay === false) {
      console.log('cleaning')
      clearInterval(intv);
    }
    else {intv = setInterval(function() {
      var cv = $("#slider-range1").slider("value");
      var sdtv = addDays(strToDate(format, minDate), cv=cv+tmstp);      
      $("#slider-range1").slider("value", cv);
      $("#date-slider-1").val(sdtv.toLocaleString('ru', {
              year: 'numeric', month: 'long', day: 'numeric'}));
    }, 1000)};
  });
  
   var btn = document.getElementById("slider-1-autoplay");
   var txt = document.getElementById("meaning");
    
    document.getElementById('meaning').onchange = function enabledbtn() {
    if (txt.value.length > 0) {
    btn.disabled = false;
    } else {
    btn.disabled = true;
    }
    }
       
    const button = document.querySelector('.button');
    
    button.addEventListener('click', () => {
      button.classList.add('active');
    });


});