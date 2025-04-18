from pathlib import Path
import argparse

# 無視するディレクトリ名、ファイル名、拡張子のセット
# プロジェクトに合わせて適宜変更してください
IGNORE_DIRS = {
    '.git',
    '__pycache__',
    '.venv',            # Python仮想環境
    'node_modules',     # Node.js パッケージ
    '.vscode',          # Visual Studio Code 設定
    '.idea',            # JetBrains IDE 設定
    'build',            # ビルド成果物
    'dist',             # 配布パッケージ
    '*.egg-info',       # Python パッケージ情報
}
IGNORE_FILES = {
    '.DS_Store',        # macOS システムファイル
    'thumbs.db',        # Windows システムファイル
    '.env',             # 環境変数ファイル (内容を表示したくない場合)
}
IGNORE_EXTENSIONS = {
    # 画像ファイル
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico',
    # 動画/音声ファイル
    '.mp4', '.mov', '.avi', '.wmv', '.mp3', '.wav', '.ogg',
    # 圧縮ファイル
    '.zip', '.gz', '.tar', '.rar', '.7z',
    # バイナリ/実行ファイル
    '.pyc', '.pyo', '.exe', '.dll', '.so', '.o', '.a', '.lib',
    # ドキュメント (内容表示が難しい場合)
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    # その他
    '.lock', '.log', '.sqlite', '.db',
}

def should_ignore(path: Path) -> bool:
    """指定されたパスが無視対象かどうかを判定する"""
    # ディレクトリ名で無視
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    # ファイル名で無視
    if path.name in IGNORE_FILES:
        return True
    # 拡張子で無視
    if path.suffix.lower() in IGNORE_EXTENSIONS:
        return True
    return False

def generate_tree(start_path: Path, prefix: str = '', is_last: bool = True) -> str:
    """ディレクトリ構造をtree形式で生成する再帰関数"""
    structure = ""
    # 無視対象のディレクトリ/ファイルは処理しない
    if should_ignore(start_path):
        return ""

    connector = '└── ' if is_last else '├── '
    structure += f"{prefix}{connector}{start_path.name}\n"

    if start_path.is_dir():
        new_prefix = prefix + ('    ' if is_last else '│   ')
        # ディレクトリ内のアイテムを取得し、無視対象を除外してソート
        items = sorted(
            [item for item in start_path.iterdir() if not should_ignore(item)],
            key=lambda x: (x.is_file(), x.name.lower()) # ディレクトリを先に、次にファイル名でソート
        )
        for i, item in enumerate(items):
            is_last_item = (i == len(items) - 1)
            structure += generate_tree(item, new_prefix, is_last_item)

    return structure

def get_file_contents(root_path: Path) -> str:
    """指定されたディレクトリ以下の全ファイルのパスと内容を行番号付きで取得する"""
    contents = ""
    separator = "-" * 80 + "\n"
    processed_files_count = 0

    # rglob で再帰的にファイルを取得し、パスでソート
    all_paths = sorted([p for p in root_path.rglob('*')])

    for item in all_paths:
        # 無視対象をスキップ
        if should_ignore(item):
            continue

        if item.is_file():
            processed_files_count += 1
            # ルートパスからの相対パスを取得し、先頭に / を追加
            try:
                relative_path = item.relative_to(root_path)
                contents += f"\n/{relative_path}:\n"
            except ValueError:
                # root_path自身がファイルの場合など
                contents += f"\n/{item.name}:\n"

            contents += separator
            try:
                # さまざまなエンコーディングに対応し、エラーは無視
                with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    if not lines:
                        contents += " [空ファイル]\n"
                    else:
                        # 行番号の桁数を計算
                        max_digits = len(str(len(lines)))
                        for i, line in enumerate(lines):
                            # 行番号を右寄せでフォーマット
                            line_num_str = str(i + 1).rjust(max_digits)
                            # 末尾の改行は維持しつつ、余分な空白は削除
                            contents += f"{line_num_str} | {line.rstrip()}\n"
            except Exception as e:
                contents += f" [エラー] ファイル読み込み中にエラーが発生しました: {e}\n"
            contents += separator

    if processed_files_count == 0:
        contents += "\n[指定されたディレクトリ内に処理対象ファイルが見つかりませんでした]\n"

    return contents

def generate_directory_listing(directory_path: str, output_file: str) -> None:
    """ディレクトリ構造とファイル内容を指定ファイルに出力する"""
    start_path = Path(directory_path).resolve() # 絶対パスに変換
    if not start_path.is_dir():
        print(f"エラー: '{directory_path}' は有効なディレクトリではありません。")
        return

    print(f"処理を開始します: {start_path}")
    print(f"出力ファイル: {output_file}")

    # ディレクトリ構造の取得 (tree形式)
    print("ディレクトリ構造を生成中...")
    # ルートディレクトリ自体も表示するために少し調整
    structure = f"{start_path.name}\n"
    items = sorted(
        [item for item in start_path.iterdir() if not should_ignore(item)],
         key=lambda x: (x.is_file(), x.name.lower())
    )
    for i, item in enumerate(items):
        is_last_item = (i == len(items) - 1)
        structure += generate_tree(item, '', is_last_item)
    print("ディレクトリ構造の生成完了。")

    # ファイル内容の取得
    print("ファイル内容を取得中...")
    file_contents_data = get_file_contents(start_path)
    print("ファイル内容の取得完了。")

    # ファイルへの書き込み
    print("ファイルに書き込み中...")
    try:
        # 出力ファイルのディレクトリが存在しない場合は作成
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(structure)
            f.write("\n\n") # treeと内容の間に空行を入れる
            f.write(file_contents_data)
        print(f"ディレクトリリストが '{output_path.resolve()}' に出力されました。")
    except IOError as e:
        print(f"エラー: ファイル '{output_file}' に書き込めませんでした: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

# --- コマンドライン引数の処理とメイン実行部分 ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="指定されたディレクトリの構造とファイル内容をリスト化してテキストファイルに出力します。")
    parser.add_argument("directory", help="リスト化するディレクトリのパス")
    parser.add_argument("output", help="出力するテキストファイル名")

    args = parser.parse_args()

    generate_directory_listing(args.directory, args.output)