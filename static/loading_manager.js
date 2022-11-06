ymaps.ready(function () {
    
    
    var start_time = document.getElementById('start').value;
    var finish_time = document.getElementById('finish').value;
    var maptype = 'False' /*$('#maptype').val();*/
    let checkedValue = [0];
          $("input[class='messageCheckbox']:checked").each(function(){
            checkedValue.push($(this).val());
          });
                            
    checkedValue = checkedValue.join()
    var data_url = `/getGeoObject/tile?bbox=%b&start_time=${start_time}&finish_time=${finish_time}&maptype=${maptype}&problems=${checkedValue}&isproblem=all`
    console.log(data_url)
    

    document.getElementById('dt_submit').onclick = function () {
        start_time = document.getElementById('start').value;
        finish_time = document.getElementById('finish').value;
        search_line = document.getElementById('searchbar').value;
        
        /*var maptype = $('#maptype').val();*/
        let checkedValue = [0];
              $("input[class='messageCheckbox']:checked").each(function(){
                checkedValue.push($(this).val());
              });
              
        let isProblem = [];
              $("input[class='isProblem']:checked").each(function(){
                isProblem.push($(this).val());
              }); 
              
        checkedValue = checkedValue.join()
        var new_url = `/getGeoObject/tile?bbox=%b&start_time=${start_time}&finish_time=${finish_time}&maptype=${maptype}&problems=${checkedValue}`
        if (search_line.length) { new_url=new_url+`&problemnum=`+encodeURIComponent(search_line) }
        if (isProblem.length==2) { new_url=new_url+`&isproblem=all`}
        if (isProblem.length==1) { new_url=new_url+`&isproblem=`+isProblem.toString()}
        if (isProblem.length==0) {new_url=new_url+`&isproblem=None`}
        
        console.log(new_url)
        
        loadingObjectManager.setUrlTemplate(new_url)
        loadingObjectManager.reloadData()
        setTimeout(function() { if ((Object.keys(loadingObjectManager.objects._objectsById).length > 0) &&  (isProblem == 'True'))  {myMap.setBounds(myMap.geoObjects.getBounds())} 
        }, 2000);

    }
    
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

    var myMap = new ymaps.Map('map-test', {
            center: [55.751574, 37.573856],
            zoom: 15,
            controls: [inputSearch, 'typeSelector', 'fullscreenControl', 'zoomControl']
        }, {minZoom: 11,
            maxZoom: 17
        }),
        loadingObjectManager = new ymaps.LoadingObjectManager(data_url, {
            clusterize: true,
            clusterDisableClickZoom: true,
            clusterIconLayout: "default#pieChart",
                   });
                    
              
    myMap.geoObjects.add(loadingObjectManager);
    
    var listBoxItems = ['Заявки с проблемами', 'Заявки без проблем']
        .map(function (title) {
            return new ymaps.control.ListBoxItem({
                data: {
                    content: title
                },
                state: {
                    selected: true
                }
            })
        }),
            reducer = function (filters, filter) {
            filters[filter.data.get('content')] = filter.isSelected();
            return filters;
        },
        // Теперь создадим список, содержащий 2 пункта.
        listBoxControl = new ymaps.control.ListBox({
            data: {
                content: 'Фильтр',
                title: 'Фильтр'
            },
            items: listBoxItems,
            state: {
                // Признак, развернут ли список.
                expanded: true,
                filters: listBoxItems.reduce(reducer, {})
            }
        });
        myMap.controls.add(listBoxControl);
        
        listBoxControl.events.add(['select', 'deselect'], function (e) {
            var listBoxItem = e.get('target');
            var filters = ymaps.util.extend({}, listBoxControl.state.get('filters'));
            filters[listBoxItem.data.get('content')] = listBoxItem.isSelected();
            listBoxControl.state.set('filters', filters);
        });
        var filterMonitor = new ymaps.Monitor(listBoxControl.state);
        filterMonitor.add('filters', function (filters) {
            // Применим фильтр.
            loadingObjectManager.setFilter(getFilterFunction(filters));
        });

        function getFilterFunction(categories) {
            return function (obj) {
                var content = obj.properties.hasProblem;
                return categories[content]
            }
        }

    loadingObjectManager.objects.events.add('balloonopen', function (e) {
        // Получим объект, на котором открылся балун.
        var id = e.get('objectId'),
            geoObject = loadingObjectManager.objects.getById(id);
        // Загрузим данные для объекта при необходимости.
        downloadContent([geoObject], id);
    });
    
    loadingObjectManager.clusters.events.add('balloonopen', function (e) {
        // Получим id кластера, на котором открылся балун.
        var id = e.get('objectId'),
        // Получим геообъекты внутри кластера.
            cluster = loadingObjectManager.clusters.getById(id),
            geoObjects = cluster.properties.geoObjects;
        // Загрузим данные для объектов при необходимости.
        downloadContent(geoObjects, id, true);
    });

    function downloadContent(geoObjects, id, isCluster) {
        
        if (document.getElementById('checkbox_toggle').checked) {$("#side_panel").html("");}
        var array1 = geoObjects.filter(function (geoObject) {
                    return geoObject.properties.balloonContentBody !== 'идет загрузка...';
                })
        array1.forEach(function (item) {
                                            $(`<p style="border-width:3px; line-height: 1.1; border-style:solid; border-color:${item.properties.border_color}; padding: 1em;">
                                            ${item.properties.balloonContentHeader}<br>
                                            ${item.properties.balloonContentBody}<br>
                                            ${item.properties.balloonAdditional}<br>
                                            ${item.properties.balloonContentFooter}<br>
                                            </p>`).hide().prependTo("#side_panel").fadeIn("slow");
        
        });        
        
        // Создадим массив меток, для которых данные ещё не загружены.
        var array = geoObjects.filter(function (geoObject) {
                    return geoObject.properties.balloonContentBody === 'идет загрузка...' ||
                        geoObject.properties.balloonContentBody === 'Not found';
                }),
        // Формируем массив идентификаторов, который будет передан серверу.
            ids = array.map(function (geoObject) {
                    return geoObject.id;
                });
        


                   
        if (ids.length) {
            console.log("request following ids from DB: ",ids) 
            // Запрос к серверу.
            // Сервер обработает массив идентификаторов и на его основе
            // вернет JSON-объект, содержащий текст балуна для
            // заданных меток.
            ymaps.vow.resolve($.ajax({
                    contentType: 'application/json',
                    type: 'POST',
                    data: JSON.stringify(ids),
                    url: '/load_additional_data',
                    dataType: 'json',
                    processData: false
                })).then(
                    function (data) {
                        let dictionary = Object.assign({}, ...data.map((x) => ({[x.id]:{'balloonContentHeader':x.balloonContentHeader, 'balloonContentBody':x.balloonContentBody,
                        'balloonContentFooter':x.balloonContentFooter, 'balloonAdditional':x.balloonAdditional, 'balloonAdditional':x.balloonAdditional}})))
                        geoObjects.forEach(function (geoObject) {
                            // Содержимое балуна берем из данных, полученных от сервера.
                            // Сервер возвращает массив объектов вида:
                            // [ {"balloonContent": "Содержимое балуна"}, ...]
                            geoObject.properties.balloonContentHeader = dictionary[geoObject.id]['balloonContentHeader'];
                            geoObject.properties.balloonContentBody = dictionary[geoObject.id]['balloonContentBody'];
                            geoObject.properties.balloonContentFooter = dictionary[geoObject.id]['balloonContentFooter'];
                          $(`<p style="border-width:3px; line-height: 1.1; border-style:solid; border-color:${geoObject.properties.border_color}; padding: 1em;">
                          ${dictionary[geoObject.id]['balloonContentHeader']}<br>
                          ${dictionary[geoObject.id]['balloonContentBody']}<br>
                          ${dictionary[geoObject.id]['balloonAdditional']}<br>
                          ${dictionary[geoObject.id]['balloonContentFooter']}<br>
                          </p>`).hide().prependTo("#side_panel").fadeIn("slow");
                        });
                        // Оповещаем балун, что нужно применить новые данные.
                        setNewData();
                    }, function () {
                        geoObjects.forEach(function (geoObject) {
                            geoObject.properties.balloonContentBody = 'Not found';
                        });
                        // Оповещаем балун, что нужно применить новые данные.
                        setNewData();
                    }
                );
        }

        function setNewData(){
            if (isCluster && loadingObjectManager.clusters.balloon.isOpen(id)) {
                loadingObjectManager.clusters.balloon.setData(loadingObjectManager.clusters.balloon.getData());
            } else if (loadingObjectManager.objects.balloon.isOpen(id)) {
                loadingObjectManager.objects.balloon.setData(loadingObjectManager.objects.balloon.getData());
            }
        }
    }
    
});





