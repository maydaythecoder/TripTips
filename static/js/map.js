// Initialize the map
const map = L.map('map').setView([0, 0], 2);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Add zoom control
L.control.zoom({
    position: 'topright'
}).addTo(map);

// Geocoding function using OpenStreetMap's Nominatim
async function geocodeCity(cityName) {
    const endpoint = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(cityName)}`;
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Accept-Language': 'en',
                'User-Agent': 'TravelTips/1.0'
            }
        });
        const data = await response.json();

        if (data && data.length > 0) {
            const location = data[0];
            return {
                lat: parseFloat(location.lat),
                lng: parseFloat(location.lon),
                placeName: location.display_name
            };
        }
        return null;
    } catch (error) {
        console.error('Geocoding error:', error);
        return null;
    }
}

// City search handler
document.getElementById('citySearch')?.addEventListener('input', async (e) => {
    const cityName = e.target.value;
    if (cityName.length > 2) {
        const location = await geocodeCity(cityName);
        if (location) {
            document.getElementById('latitude').value = location.lat;
            document.getElementById('longitude').value = location.lng;
            document.getElementById('name').value = location.placeName;
        }
    }
});

// Load locations from the API
fetch('/api/locations')
    .then(response => response.json())
    .then(locations => {
        locations.forEach(location => {
            const marker = L.marker([location.latitude, location.longitude])
                .bindPopup(`
                    <h4>${location.name}</h4>
                    <p>Rating: ${'★'.repeat(location.rating)}</p>
                `)
                .addTo(map);
        });
    });

// Click handler for adding new locations
map.on('click', (e) => {
    document.getElementById('latitude').value = e.latlng.lat;
    document.getElementById('longitude').value = e.latlng.lng;
});