const videoElement = document.getElementById('video');

navigator.mediaDevices
    .getUserMedia({ video: true })
    .then(stream => {
        console.log('Webcam access granted');

        const socket = new WebSocket('ws://localhost:8080');

        const webcamStream = new Uint8Array(stream);

        socket.onopen = () => {
            console.log('WebSocket connection established');

            // Start sending webcam feed to Python script
            setInterval(() => {
                socket.send(webcamStream);
            }, 1000 / 30); // Send webcam feed every 30 frames (30fps)
        };

        socket.onmessage = (event) => {
            console.log('Received message from Python script:', event.data);

            // Process face recognition results
            // Display face recognition results on web page
        };
    })
    .catch(err => {
        console.error('Error accessing webcam:', err);
    });