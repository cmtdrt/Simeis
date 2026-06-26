FROM rust:1.88.0-trixie

WORKDIR /app

# On copie tout le projet filtré par .dockerignore
COPY . .

# compio (io_uring) ne fonctionne pas dans Docker (seccomp) : on compile avec tokio
RUN cargo build --release --package simeis-server --no-default-features --features tokio \
    && cp target/release/simeis-server /usr/local/bin/simeis-server

# Le serveur écoute sur 0.0.0.0:3333 (voir simeis-server/src/main.rs)
EXPOSE 3333

ENTRYPOINT ["simeis-server"]
