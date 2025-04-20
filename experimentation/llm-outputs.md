```markdown
# Repository Reader

## プロジェクトの概要

このリポジトリは、指定されたディレクトリの構造とファイルの内容をテキスト形式で出力するツールです。
大規模なプロジェクトの構造を把握したり、ドキュメント生成の補助として利用することを想定しています。
LangchainとGoogle Gemini APIを使用し、リポジトリの情報を基に、READMEなどのドキュメントを自動生成する機能も備えています。

## 開発環境の構築手順

以下の手順で開発環境を構築します。

1.  **必要なツールのインストール:**

    *   [Docker](https://www.docker.com/)
    *   [Docker Compose](https://docs.docker.com/compose/)
    *   [Taskfile](https://taskfile.dev/)

2.  **リポジトリのクローン:**

    ```bash
    git clone <リポジトリのURL>
    cd repository-reader
    ```

3.  **.envファイルの作成:**

    リポジトリのルートディレクトリに`.env`ファイルを作成し、必要な環境変数を設定します。
    セキュリティ上の理由から、このファイルはリポジトリには含まれていません。
    必要な環境変数は以下の通りです。

    *   `POETRY_VERSION`: Poetryのバージョン (例: `1.7.1`)
    *   `POETRY_HOME`: Poetryのインストール先 (例: `/opt/poetry`)
    *   `USER_UID`: ユーザーのUID (例: `1000`)
    *   `USERNAME`: ユーザー名 (例: `dev`)
    *   `PROJECT_NAME`: プロジェクト名 (例: `repository-reader`)
    *   `CONTAINER_NAME`: コンテナ名 (例: `repository-reader-dev`)

    ```bash
    touch .env
    ```

4.  **UIDとUSERNAMEを.envに書き込み:**
    ```bash
    task write_uid_onto_env
    ```

5.  **Dockerコンテナの起動:**

    Taskfileを使用することで、Dockerイメージのビルドからコンテナの起動までを簡単に行うことができます。

    ```bash
    task shell
    ```

    このコマンドは、以下の処理を順番に実行します。

    1.  `write_uid_onto_env`: ホストマシンのUIDとUSERNAMEを`.env`ファイルに書き込みます。
    2.  `build`: `docker-compose.yaml`ファイルを使用してDockerイメージをビルドします。
    3.  `up`: Dockerコンテナを起動します。
    4.  `docker exec`: 起動したコンテナにログインします。

## フォルダ構成

```
repository-reader/
├── context/                      # Dockerコンテナの定義ファイル
│   ├── cpu/
│   │   └── docker-compose.yaml  # Docker Composeファイル（CPU環境用）
│   └── Dockerfile              # DockerイメージのDockerfile
├── experimentation/            # 実験的なコードやスクリプト
│   ├── rag.py                  # RAG(Retrieval Augmented Generation)の実験用スクリプト
│   └── llm-outputs.md          # RAGの出力先
├── project_module/             # プロジェクトのメインモジュール
│   └── src/
│       └── project_module/
│           ├── directory_lister/    # ディレクトリ構造をリスト化するモジュール
│           │   ├── temp_lister_test/  # directory_listerのテスト用ファイル
│           │   │   ├── dir_a/
│           │   │   ├── dir_c/
│           │   │   ├── File_B.py
│   │           │   └── file_z.txt
│           │   ├── __init__.py
│           │   ├── directory_lister.py # ディレクトリ構造リスト化のメイン処理
│           │   ├── ignore_config.py  # 無視するファイルやディレクトリの設定
│           │   └── ignore_settings.yml # 無視設定ファイル
│           └── __init__.py
├── .gitignore                  # Gitで管理しないファイルの設定
├── pyproject.toml              # Poetryの設定ファイル
├── README.md                   # プロジェクトのREADME
└── Taskfile.yaml               # Taskfileの設定ファイル

```

*   **context:** Dockerコンテナの構築に必要なファイルが含まれています。`Dockerfile`はPythonの開発環境を構築し、`docker-compose.yaml`はコンテナの起動設定を定義します。
*   **experimentation:** RAGの実験に使用するスクリプトやテキストファイルが含まれています。
*   **project\_module:** プロジェクトのメインとなるモジュールが含まれています。
    *   **directory\_lister:** ディレクトリ構造をリスト化する機能を提供するモジュールです。
        *   `directory_lister.py`: ディレクトリ構造を走査し、ファイルとディレクトリの情報を収集する主要なスクリプトです。
        *   `ignore\_config.py`: 無視するファイルやディレクトリのパターンを定義するための設定を管理します。
        *   `ignore\_settings.yml`: 無視するファイルやディレクトリの具体的な設定を記述します。
*   **.gitignore:** Gitで管理しないファイルやディレクトリを指定します。
*   **pyproject.toml:** Poetryのプロジェクト設定ファイルです。依存関係やプロジェクトのメタ情報が記述されています。
*   **README.md:** プロジェクトの概要や使い方を説明するファイルです。
*   **Taskfile.yaml:** Taskfileの設定ファイルです。Dockerコンテナのビルドや起動などのタスクを定義します。

## どこでどんな処理がなされているか

*   **`project_module/src/project_module/directory_lister/directory_lister.py`:**
    *   `DirectoryLister`クラスが定義されており、以下の処理を行います。
        *   指定されたディレクトリを走査し、ファイルとディレクトリの情報を収集します。
        *   `ignore_settings.yml`に基づいて、無視するファイルやディレクトリをフィルタリングします。
        *   ディレクトリ構造をtree形式で出力します。
        *   ファイルの内容を行番号付きで出力します。
*   **`experimentation/rag.py`:**
    *   `DirectoryLister`を使用してリポジトリの構造とコードを取得します。
    *   取得した情報をLangchainとGoogle Gemini APIに渡し、READMEを自動生成します。
*   **`context/Dockerfile`:**
    *   Python 3.11をベースにしたDockerイメージを構築します。
    *   PoetryとNode.jsをインストールします。
    *   開発用のユーザーを作成し、必要な環境変数を設定します。
*   **`Taskfile.yaml`:**
    *   `build`: `docker-compose.yaml`を元にDockerイメージをビルドします。
    *   `up`:  `docker-compose.yaml`を元にDockerコンテナを起動します。
    *   `down`: 起動しているDockerコンテナを停止し、削除します。
    *   `write_uid_onto_env`:  `.env`ファイルにホストマシンのUIDとUSERNAMEを書き込みます。
    *   `shell`:  上記のタスクを順番に実行し、コンテナにログインします。

## 使い方

1.  **開発環境の構築:** 上記の「開発環境の構築手順」に従って環境を構築します。
2.  **環境変数の設定:** `.env`ファイルに必要な環境変数を設定します。特に、Google Gemini APIを使用する場合は、APIキーを設定する必要があります。
3.  **スクリプトの実行:**

    *   リポジトリ全体の構造とコードをテキストファイルに出力するには、`project_module/src/project_module/directory_lister/directory_lister.py`を実行します。

        ```bash
        # コンテナに入っている状態で実行
        python project_module/src/project_module/directory_lister/directory_lister.py
        ```

        出力ファイルは`text.txt`として保存されます。

    *   RAGを使用してREADMEを自動生成するには、`experimentation/rag.py`を実行します。

        ```bash
        # コンテナに入っている状態で実行
        python experimentation/rag.py
        ```

        生成されたREADMEの内容は、コンソールに出力されるとともに、`llm-outputs.md`ファイルに保存されます。

## 処理フロー

### DirectoryLister

```mermaid
graph LR
    A[開始] --> B{設定ファイルの読み込み (ignore_settings.yml)};
    B --> C{DirectoryListerのインスタンス化};
    C --> D{ディレクトリ構造の生成};
    D --> E{ファイル内容の生成};
    E --> F{ファイルへ書き込み (text.txt)};
    F --> G[終了];
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#f9f,stroke:#333,stroke-width:2px
```

### RAG

```mermaid
graph LR
    A[開始] --> B{設定ファイルの読み込み (ignore_settings.yml)};
    B --> C{DirectoryListerのインスタンス化};
    C --> D{ディレクトリ構造の生成};
    D --> E{ファイル内容の生成};
    E --> F{ファイルへ書き込み (text.txt)};
    F --> G{テキストファイルの読み込み};
    G --> H{Gemini APIへのプロンプト送信};
    H --> I{README生成};
    I --> J{READMEのファイルへ書き出し (llm-outputs.md)};
    J --> K[終了];
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style K fill:#f9f,stroke:#333,stroke-width:2px
```

**フローの説明:**

1.  **設定ファイルの読み込み:** `ignore_settings.yml`を読み込み、無視するファイルやディレクトリの設定を取得します。
2.  **DirectoryListerのインスタンス化:** 読み込んだ設定を基に、`DirectoryLister`クラスのインスタンスを作成します。
3.  **ディレクトリ構造の生成:** `DirectoryLister`を使用して、指定されたディレクトリの構造をtree形式で生成します。
4.  **ファイル内容の生成:** `DirectoryLister`を使用して、指定されたディレクトリ内の各ファイルの内容を行番号付きで生成します。
5.  **ファイルへ書き込み:** 生成されたディレクトリ構造とファイルの内容を`text.txt`ファイルに書き込みます。
6.  **テキストファイルの読み込み:**  `text.txt`ファイルの内容を読み込みます。
7.  **Gemini APIへのプロンプト送信:** 読み込んだファイルの内容と、README生成を指示するプロンプトをGemini APIへ送信します。
8.  **README生成:** Gemini APIからの応答に基づき、READMEの内容を生成します。
9.  **READMEのファイルへ書き出し:** 生成されたREADMEの内容を`llm-outputs.md`ファイルに書き出します。
10. **終了:** 処理を終了します。
```