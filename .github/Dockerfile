FROM rust:1.85.0-bookworm AS builder

WORKDIR /app

COPY Cargo.toml Cargo.lock ./
COPY simeis-data/Cargo.toml simeis-data/
COPY simeis-server/Cargo.toml simeis-server/
COPY simeis-server/.cargo/config.toml simeis-server/.cargo/config.toml

COPY simeis-data/src simeis-data/src
COPY simeis-server/src simeis-server/src

RUN cargo build --release --package simeis-server

FROM debian:bookworm-slim

WORKDIR /app

COPY --from=builder /app/target/release/simeis-server /app/simeis-server

EXPOSE 3333

ENTRYPOINT ["/app/simeis-server"]
