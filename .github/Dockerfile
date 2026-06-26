FROM rust:1.88.0-trixie

WORKDIR /app

# On copie tout le projet filtré par .dockerignore
COPY . .

# On compile le serveur en mode release et on copie le binaire dans le conteneur
RUN cargo build --release --package simeis-server \
    && cp target/release/simeis-server /app/simeis-server

# Le serveur écoute sur 0.0.0.0:3333 (voir simeis-server/src/main.rs)
EXPOSE 3333

ENTRYPOINT ["/app/simeis-server"]
