FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

# -----------------------------------------------------------------
# Copy certificates to make use of free open ai usage within the lab
# REMOVE THIS WHEN DEPLOYING TO CODE ENGINE

# Copy the self-signed root CA certificate into the container
COPY certs/rootCA.crt /usr/local/share/ca-certificates/rootCA.crt

# Update the CA trust store to trust the self-signed certificate
# Set the permissions for the certificate file and update the CA certificates
# This is necessary to allow the container to trust the self-signed certificate 
# when making requests to the OpenAI API, which is required for free usage within 
# the lab environment. When deploying to Code Engine, this step can be removed as 
# the environment will have proper certificates in place.

# Performs two sequential operations inside the image during build. The && ensures 
# the second command runs only if the first succeeds.

# 644 is an octal permission setting that allows the owner to read and write the file, while
# group members and others can only read the file. This is a common permission setting for 
# certificate files.
# Owner: read (4) + write (2) = 6
# Group: read (4) = 4
# Others: read (4) = 4

RUN chmod 644 /usr/local/share/ca-certificates/rootCA.crt && \
  update-ca-certificates

# Set the environment variable OPENAI_API_KEY to empty string
ENV OPENAI_API_KEY=skills-network
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
# -----------------------------------------------------------------

CMD ["python", "-u", "server.py"]