FROM rust:1.88.0-trixie

WORKDIR /app

# On copie tout le projet filtré par .dockerignore (target/, doc/, etc.)
COPY . .

RUN cargo build --release --package simeis-server

ENTRYPOINT ["/app/target/release/simeis-server"]
