let chartCanvas = document.getElementById("trafficChart");
let ctx = chartCanvas.getContext("2d");

let laneDataHistory = {
    "Lane A": [],
    "Lane B": [],
    "Lane C": [],
    "Lane D": []
};

function drawChart() {
    ctx.clearRect(0, 0, chartCanvas.width, chartCanvas.height);

    ctx.fillStyle = "white";
    ctx.font = "14px Arial";
    ctx.fillText("Vehicle Count (Last 10 Updates)", 10, 20);

    let lanes = Object.keys(laneDataHistory);
    let maxPoints = 10;

    let xStep = chartCanvas.width / maxPoints;

    lanes.forEach((lane, index) => {
        let values = laneDataHistory[lane];

        ctx.beginPath();
        ctx.lineWidth = 2;

        // Different color for each lane
        let colors = ["#00ff99", "#ffdd57", "#ff4d4d", "#00ccff"];
        ctx.strokeStyle = colors[index];

        for (let i = 0; i < values.length; i++) {
            let x = i * xStep;
            let y = chartCanvas.height - (values[i] * 3);  // scale factor

            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }

        ctx.stroke();
        ctx.closePath();

        ctx.fillStyle = colors[index];
        ctx.fillText(lane, 10, 40 + index * 20);
    });
}

function updateTrafficLight(signalState) {
    document.getElementById("redLight").classList.remove("active");
    document.getElementById("yellowLight").classList.remove("active");
    document.getElementById("greenLight").classList.remove("active");

    // If any lane is GREEN, show green light
    let greenExists = Object.values(signalState).includes("GREEN");

    if (greenExists) {
        document.getElementById("greenLight").classList.add("active");
    } else {
        document.getElementById("redLight").classList.add("active");
    }
}

async function fetchStatus() {
    let res = await fetch("/status");
    let data = await res.json();

    // Vehicle Density UI
    let densityHTML = "";
    for (let lane in data.vehicle_counts) {
        let count = data.vehicle_counts[lane];
        let percent = Math.min((count / 50) * 100, 100);

        densityHTML += `
            <div class="density-card">
                <b>${lane}</b> : ${count} vehicles
                <div class="progress">
                    <div class="progress-bar" style="width:${percent}%"></div>
                </div>
            </div>
        `;
    }
    document.getElementById("densityCards").innerHTML = densityHTML;

    // Signal UI
    let signalHTML = "";
    for (let lane in data.signal_state) {
        let state = data.signal_state[lane];

        signalHTML += `
            <div class="signal-card">
                <b>${lane}</b> : 
                <span style="color:${state === "GREEN" ? "#00ff99" : "red"}">
                    ${state}
                </span>
            </div>
        `;
    }
    document.getElementById("signalCards").innerHTML = signalHTML;

    document.getElementById("currentLane").innerHTML =
        `🟢 Current GREEN Lane: <b>${data.current_lane}</b>`;

    document.getElementById("greenTime").innerHTML =
        `⏱ Green Duration: <b>${data.green_time}</b> seconds`;

    // Ambulance Status UI
    if (data.ambulance_mode) {
        document.getElementById("ambulanceStatus").innerHTML =
            `🚑 GREEN CORRIDOR ACTIVE ON <b>${data.ambulance_lane}</b>`;
    } else {
        document.getElementById("ambulanceStatus").innerHTML =
            `✅ Normal Adaptive Mode Running`;
    }

    // Update traffic light animation
    updateTrafficLight(data.signal_state);

    // Update chart data history
    for (let lane in data.vehicle_counts) {
        laneDataHistory[lane].push(data.vehicle_counts[lane]);

        if (laneDataHistory[lane].length > 10) {
            laneDataHistory[lane].shift();
        }
    }

    drawChart();
}

async function enableAmbulance() {
    let lane = document.getElementById("laneSelect").value;

    let res = await fetch("/ambulance", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({lane: lane})
    });

    let data = await res.json();
    alert(data.message);

    document.getElementById("ambulanceStatus").innerHTML =
        `🚑 GREEN CORRIDOR ACTIVATED FOR <b>${lane}</b>`;
}

async function clearAmbulance() {
    let res = await fetch("/clear_ambulance", {method: "POST"});
    let data = await res.json();
    alert(data.message);

    document.getElementById("ambulanceStatus").innerHTML =
        `✅ Ambulance Mode Cleared. Normal Traffic Running.`;
}

setInterval(fetchStatus, 1000);
fetchStatus();
let map = L.map("map").setView([17.3850, 78.4867], 13); // default Hyderabad
let marker;

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors"
}).addTo(map);

marker = L.marker([17.3850, 78.4867]).addTo(map)
    .bindPopup("🚑 Ambulance")
    .openPopup();

async function fetchGPS() {
    let res = await fetch("/gps");
    let data = await res.json();

    let lat = data.lat;
    let lon = data.lon;

    marker.setLatLng([lat, lon]);
    map.setView([lat, lon], 15);

    marker.bindPopup(`🚑 Ambulance<br>Lat: ${lat}<br>Lon: ${lon}`).openPopup();
}

setInterval(fetchGPS, 2000);

