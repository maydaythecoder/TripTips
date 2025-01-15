mapboxgl.accessToken = 'YOUR_MAPBOX_TOKEN'; // Replace with your Mapbox token

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/dark-v10',
    center: [-74.5, 40],
    zoom: 2
});

map.addControl(new mapboxgl.NavigationControl());

// Load locations from the API
fetch('/api/locations')
    .then(response => response.json())
    .then(locations => {
        locations.forEach(location => {
            const marker = new mapboxgl.Marker()
                .setLngLat([location.longitude, location.latitude])
                .setPopup(new mapboxgl.Popup().setHTML(`
                    <h4>${location.name}</h4>
                    <p>Rating: ${'★'.repeat(location.rating)}</p>
                `))
                .addTo(map);
        });
    });

// Click handler for adding new locations
map.on('click', (e) => {
    const coords = e.lngLat;
    document.getElementById('latitude').value = coords.lat;
    document.getElementById('longitude').value = coords.lng;
});
