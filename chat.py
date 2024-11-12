import random
import json

import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = 'data.pth'
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Ask"

def get_response(msg):
    sentence = tokenize(msg)
    print(f"Tokenized sentence: {sentence}")  # Debugging

    X = bag_of_words(sentence, all_words)
    print(f"Bag of words: {X}")  # Debugging

    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device).float() # Ensure X is of float type

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    print(f"Predicted tag index: {predicted.item()}")  # Debugging


    tag = tags[predicted.item()]
    print(f"Predicted tag: {tag}")  # Debugging


    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    print(f"Prediction confidence: {prob.item()}")  # Debugging

    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    
    return "I do not understand..."

if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        # sentence
        sentence = input("You: ")
        if sentence.lower() == "quit":
            break

        resp = get_response(sentence)
        print(resp)
