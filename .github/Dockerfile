FROM rust:1.85.0-bookworm

WORKDIR /app

# On copie tout le projet filtré par .dockerignore (target/, doc/, etc.)
COPY . .

RUN cargo build --release --package simeis-server

ENTRYPOINT ["/app/target/release/simeis-server"]
