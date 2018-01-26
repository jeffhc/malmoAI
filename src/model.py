from keras.models import Sequential
from keras.layers import Dense
import numpy
# fix random seed for reproducibility
numpy.random.seed(7)


# Load data set
dataset = numpy.loadtxt("data.csv", delimiter=",")
# split into input (X) and output (Y) variables
X = dataset[:,0:4]
Y = dataset[:,4]

# Make the Y one-hot
new = []
for value in Y:
    onehot = [0]*7
    onehot[int(value)] = 1
    new.append(onehot)
Y = numpy.asarray(new)

# create model
model = Sequential()
model.add(Dense(12, input_dim=4, activation='relu'))
model.add(Dense(8, activation='relu'))
model.add(Dense(7, activation='sigmoid')) # 7 different possible actions


# Compile model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Fit the model
model.fit(X, Y, epochs=150, batch_size=10)

# evaluate the model
scores = model.evaluate(X, Y)
print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))


# serialize model to JSON
model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("model.h5")
print("Saved model to disk")
