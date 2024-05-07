
import torch
import torch.nn as nn
import torch.optim as optim
from torchtext.data import Field, LabelField, BucketIterator
from torchtext.datasets import IMDB
from torchtext.vocab import Vocab

# Define the fields for text and labels
TEXT = Field(tokenize='spacy', lower=True)
LABEL = LabelField(dtype=torch.float)

# Load the IMDb dataset
train_data, test_data = IMDB.splits(TEXT, LABEL)

# Build vocabulary
TEXT.build_vocab(train_data, max_size=25000, vectors="glove.6B.100d")  # You can specify pretrained word embeddings
LABEL.build_vocab(train_data)

# Create iterators
BATCH_SIZE = 64
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
train_iterator, test_iterator = BucketIterator.splits(
    (train_data, test_data),
    batch_size=BATCH_SIZE,
    device=device
)

# Define the model architecture
class RNN(nn.Module):
    def __init__(self, input_dim, embedding_dim, hidden_dim, output_dim):
        super().__init__()
        self.embedding = nn.Embedding(input_dim, embedding_dim)
        self.rnn = nn.LSTM(embedding_dim, hidden_dim)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, text):
        embedded = self.embedding(text)
        output, (hidden, _) = self.rnn(embedded)
        return self.fc(hidden.squeeze(0))

INPUT_DIM = len(TEXT.vocab)
EMBEDDING_DIM = 100
HIDDEN_DIM = 256
OUTPUT_DIM = 1

model = RNN(INPUT_DIM, EMBEDDING_DIM, HIDDEN_DIM, OUTPUT_DIM).to(device)

# Define loss function and optimizer
criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# Train the model
def train(model, iterator, optimizer, criterion):
    model.train()
    for batch in iterator:
        optimizer.zero_grad()
        predictions = model(batch.text).squeeze(1)
        loss = criterion(predictions, batch.label)
        loss.backward()
        optimizer.step()

# Evaluate the model
def evaluate(model, iterator, criterion):
    model.eval()
    total_loss = 0
    with torch.no_grad():
        for batch in iterator:
            predictions = model(batch.text).squeeze(1)
            loss = criterion(predictions, batch.label)
            total_loss += loss.item()
    return total_loss / len(iterator)

# Train the model
N_EPOCHS = 5
for epoch in range(N_EPOCHS):
    train(model, train_iterator, optimizer, criterion)
    test_loss = evaluate(model, test_iterator, criterion)
    print(f'Epoch: {epoch+1}, Test Loss: {test_loss:.3f}')
