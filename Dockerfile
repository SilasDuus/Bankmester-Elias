# Brug et officielt Python-image
FROM python:3.11-slim

# Sæt arbejdsmappen i containeren
WORKDIR /usr/src/app

# Kopier filen for afhængigheder og installer dem
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopier ALT andet fra din lokale rodmappe til arbejdsmappen i containeren
COPY . .

# Kommandoen, der starter botten. Stien er essentiel.
CMD ["python3", "Discord Bot/main.py"]