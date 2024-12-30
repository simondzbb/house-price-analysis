// 初始化地图，设置中心为台北市
var map = new AMap.Map('container', {
    viewMode: '2D',
    zoom: 12, // 调整适合台北市的缩放等级
    center: [121.5400, 24.9700] // 台北市的中心点经纬度
});

// 定义全局变量存储当前显示的 infoBox
let currentInfoBox = null;

// 从 Excel 文件读取数据
fetch('../data/data.xlsx')
    .then(response => response.arrayBuffer())
    .then(data => {
        var workbook = XLSX.read(data, { type: 'array' });
        var sheetName = workbook.SheetNames[0];
        var sheet = workbook.Sheets[sheetName];

        // 解析为 JSON 格式
        var jsonData = XLSX.utils.sheet_to_json(sheet);

        var cityData = [];  // 存储台北市所有数据
        var totalPrice = 0;
        var totalCount = 0;

        jsonData.forEach(item => {
            var longitude = parseFloat(item['经度']);
            var latitude = parseFloat(item['纬度']);
            var price = parseFloat(item['房价']);
            var age = parseFloat(item['房龄']);
            var subwayDistance = item['最近地铁距离'];
            var supermarketCount = item['周围商超数量'];

            if (!isNaN(longitude) && !isNaN(latitude) && !isNaN(price)) {
                var markerData = {
                    longitude: longitude,
                    latitude: latitude,
                    price: price,
                    age: age,
                    subwayDistance: subwayDistance,
                    supermarketCount: supermarketCount
                };

                // 将所有数据存入台北市的城市数据列表
                cityData.push(markerData);
                totalPrice += price;
                totalCount++;
            }
        });

        // 计算台北市的平均房价
        var avgPrice = totalPrice / totalCount;

        // 初始化时显示所有数据点
        updateMap(cityData);

        // 更新地图显示数据
        function updateMap(data) {
            map.clearMap();
            data.forEach(item => {
                var color = getMarkerColor(item.price, avgPrice);
                var marker = new AMap.Marker({
                    position: [item.longitude, item.latitude],
                    map: map,
                    icon: new AMap.Icon({
                        size: new AMap.Size(11, 11),
                        image: createGradientCircle(color),
                        imageSize: new AMap.Size(11, 11)
                    }),
                });

                marker.on('mouseover', function () {
                    marker.setTitle(`房价: ${item.price} 元/m²`);
                });

                marker.on('click', function () {
                    displayInfoBox(item);
                });
            });
        }

        // 根据房价与平均房价的对比，返回渐变色
        function getMarkerColor(price, avgPrice) {
            var ratio = (price - avgPrice) / avgPrice;
            ratio = Math.max(0, Math.min(1, ratio));
            var r = Math.floor(255 * ratio);
            var g = Math.floor(255 * (1 - ratio));
            var b = 255 - r;
            return rgbToHex(r, g, b);
        }

        function rgbToHex(r, g, b) {
            return ((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1).toUpperCase();
        }

        function createGradientCircle(color) {
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            var radius = 10;
            canvas.width = radius * 2;
            canvas.height = radius * 2;

            var gradient = ctx.createRadialGradient(radius, radius, 0, radius, radius, radius);
            gradient.addColorStop(0, 'white');
            gradient.addColorStop(1, `#${color}`);

            ctx.beginPath();
            ctx.arc(radius, radius, radius, 0, 2 * Math.PI);
            ctx.fillStyle = gradient;
            ctx.fill();

            return canvas.toDataURL();
        }

        function displayInfoBox(item) {
            // 隐藏当前的 infoBox
            if (currentInfoBox) {
                currentInfoBox.style.display = 'none';
            }

            var infoBox = document.getElementById('infoBox');
            document.getElementById('longitude').textContent = item.longitude;
            document.getElementById('latitude').textContent = item.latitude;
            document.getElementById('priceInfo').textContent = item.price;
            document.getElementById('ageInfo').textContent = item.age;
            document.getElementById('subwayDistance').textContent = item.subwayDistance || '无数据';
            document.getElementById('supermarketCount').textContent = item.supermarketCount || '无数据';
            infoBox.style.display = 'block';

            // 设置为当前显示的 infoBox
            currentInfoBox = infoBox;
        }

        // 在地图上点击时隐藏信息框
        map.on('click', function () {
            if (currentInfoBox) {
                currentInfoBox.style.display = 'none';
                currentInfoBox = null;
            }
        });
    })
    .catch(error => {
        console.error('读取或解析Excel文件失败:', error);
    });
