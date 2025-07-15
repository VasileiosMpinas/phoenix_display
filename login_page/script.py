import socket
import cv2
import deepface

socket = socket.socket()
socket.connect(("localhost", 8080))

while True:
  data = socket.recv(1024)

  # Decode webcam feed from data
  webcamFeed = deepface.decode_webcam_feed(data)

  # Perform real-time face recognition with DeepFace
  faces = deepface.detectMultiScale(webcamFeed)

  for face in faces:
    # Convert face to a tensor
    faceTensor = deepface.faceToTensor(face)

    # Predict the identity of the face using the face recognizer
    prediction = deepface.face_recognition(faceTensor)

    # Display the recognized individual and confidence score
    print(f"Recognized individual: {prediction.identity}, confidence: {prediction.confidence}")

  # Encode face recognition results
  encodedResults = encodeResults(results)

  # Send face recognition results back to web page
  socket.send(encodedResults)