# variable d'envrinnement pour le PDF manuel utilisateur
TYPST_SRC = doc/manual.typ
TYPST_OUT = doc/manuel_utilisateur.pdf

# Définition des cibles de make ( pas de conflit avec de potentiel fichiers du projet )
.PHONY: ci clean fmt-check build test doc typst

# Nettoyer fichiers de build
clean:
	cargo clean

# formattage du code et vérification du formatage
fmt-check:
	cargo fmt --check

# Rustflags pour la compilation du kernel, avec optimisation et de réduction de la taille du binaire
build:
	RUSTFLAGS="-C code-model=kernel -C strip=symbols -C codegen-units=1" cargo build --verbose

# Lancement des tests
test:
	cargo test --verbose

# Construction du PDF du manuel utilisateur à partir du fichier typst
doc:
	typst compile $(TYPST_SRC) $(TYPST_OUT)

