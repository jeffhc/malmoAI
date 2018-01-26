from keras.models import Sequential
from keras.layers import Dense
from keras.models import model_from_json
import numpy as np

# load json and create model
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model.h5")
print("Loaded model from disk")

loaded_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

prediction = loaded_model.predict(np.asarray([[2, 3, 2, 3]])) # answer is 5
biggest = int(np.amax(prediction))
answer = np.argmax(prediction)
print("Answer:", str(answer))
