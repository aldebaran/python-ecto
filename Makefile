SHELL := /bin/bash # We use bash-only features in recipes

# List of repos used by the project
PROJECTS := ecto
MANIFEST := MANIFEST.txt

# Toolchain to use for tc package
TOOLCHAIN_NAME := linux64

# ──────────────
# Build commands

.PHONY: ecto

ecto: qibuild_workspace
	@cd qibuild_ws; qibuild configure -c $(TOOLCHAIN_NAME) --release ecto
	@cd qibuild_ws; qibuild make -c $(TOOLCHAIN_NAME) -j $$((`nproc`-1)) ecto
	@cd qibuild_ws; qibuild install -c $(TOOLCHAIN_NAME) ecto ../install

# ──────────────────────
# Fetch sources commands

.PHONY: qibuild_workspace

qibuild_workspace:
	@[ -d qibuild_ws ] || mkdir -p qibuild_ws
	@cd qibuild_ws; [ -d .qi ] || qibuild init
	@cd qibuild_ws;for GIT_REPO in $(PROJECTS); do v=$$(cat ../$(MANIFEST) | grep "`echo $$GIT_REPO`_VERSION" | cut -d= -f2); u=$$(cat ../$(MANIFEST) | grep "`echo $$GIT_REPO`_URI" | cut -d= -f2); [ -d $$GIT_REPO ] || qisrc add -b $$v --src $$GIT_REPO $$u; done

# ─────────
# Packaging

.PHONY: python_package

python_package: ecto
	@python setup.py bdist_wheel