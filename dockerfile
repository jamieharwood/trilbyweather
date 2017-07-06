FROM alpine:3.5
# FROM busybox

# Update
RUN apk add --update python py-pip

# Install app dependencies
RUN pip install feedparser

# Bundle app source
COPY trilby.db /trilby.db
COPY weatherProcv002.py /sweatherProcv002.py

CMD ["python", "/weatherProcv002.py", ""]
