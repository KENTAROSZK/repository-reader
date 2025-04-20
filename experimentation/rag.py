import sys
import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI

# 自作モジュールをインポート
sys.path.append(os.path.abspath("../project_module/src/project_module"))
from directory_lister.directory_lister import DirectoryLister
from directory_lister.ignore_config import get_config, IgnoreConfig


# 検索を開始するディレクトリのパスを指定
ROOT_DIR = Path(__file__).resolve().parents[1] # 2つ上のディレクトリを取得する
# テキストファイルの出力先のパスを指定
DIR_AND_CODES_FILE = Path(__file__).resolve().parent / 'text.txt'
# 設定ファイルのパスを指定
SETTING_YML_DIR = Path(__file__).resolve().parent.parent/ "project_module/src/project_module/directory_lister" / 'ignore_settings.yml'

# 環境変数を取得
DOT_ENV_PATH = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(DOT_ENV_PATH)


def main() -> None:
    
    # インスタンス化
    lister = DirectoryLister(
        directory_path=Path(ROOT_DIR),
        output_file=Path(DIR_AND_CODES_FILE),
        config=get_config(Path(SETTING_YML_DIR))
    )

    # ディレクトリリスト化を実行
    lister.run()

    with open(DIR_AND_CODES_FILE, 'r', encoding='utf-8') as f:
        dir_and_codes: str = f.read()
    
    question: str = """
このリポジトリを公開するためのREADME.mdを作成してください。
READMEの内容は、以下の内容を含めてください。
- プロジェクトの概要
- 開発環境の構築手順
- フォルダの構成とそれぞれの簡単な説明
- どこでどんな処理がなされているか
- 使い方
- 処理フローを示すmermaid記法の図
"""
    prompt = f"""
以下の内容は、今開発しているリポジトリのコードのディレクトリとそのソースコードです。
環境変数などの設定ファイルは、セキュリティ上の理由でテキスト化していません。
質問に答えてください。

# 質問
{question}

# ディレクトリとソースコード
{dir_and_codes}
"""

    print("="*30)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash"
    )
    results = llm.invoke(prompt)
    content = results.content
    print(content)

    with open(Path("./llm-outputs.md"), 'w', encoding='utf-8') as f:
        f.write(content)


    


if __name__ == "__main__":
    main()