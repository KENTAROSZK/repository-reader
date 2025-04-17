FROM python:3.11-slim

# Build-time arguments
ARG POETRY_VERSION
ARG POETRY_HOME
ARG USER_UID
ARG USERNAME

# 必要なパッケージをインストール（curl等）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Poetryのインストール
RUN echo ${POETRY_HOME}
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org/ | python3 - --version ${POETRY_VERSION} && \
    ln -s ${POETRY_HOME}/bin/poetry /usr/local/bin/poetry

# Node.jsとnpmのインストール
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
apt-get install -y --no-install-recommends nodejs && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*


# ==========================================
# Create user in the container to avoid permission matter 
# incompatible between host and container user
# ==========================================
RUN useradd --uid ${USER_UID} -m ${USERNAME} 

USER $USERNAME
ENV PATH="/usr/local/bin:$PATH"


WORKDIR /home/${USERNAME}/