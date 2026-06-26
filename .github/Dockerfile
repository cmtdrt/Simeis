FROM rust:1.88.0-trixie

WORKDIR /app

# Contexte filtré par .dockerignore ; doc/swagger* requis par include_str! à la compilation
COPY . .

RUN cargo build --release --package simeis-server \
    && cp target/release/simeis-server /app/simeis-server

# Le serveur écoute sur 0.0.0.0:3333 (voir simeis-server/src/main.rs)
EXPOSE 3333

ENTRYPOINT ["/app/simeis-server"]
