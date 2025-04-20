from pathlib import Path
from typing import List
from config import get_config, Config

import os
import sys


class DirectoryLister:
    def __init__(
            self,
            directory_path: Path,
            output_file: Path,
            config: Config
    ):
        self.root_path = directory_path.resolve() # 絶対パスに変換
        self.output_file = output_file
        self.config = config

        if not self.root_path.is_dir():
            raise ValueError(f"{self.root_path} is not a directory.")
        
        self.ignore_dirs = getattr(self.config, "ignore_dirs")
        self.ignore_files = getattr(self.config, "ignore_files")
        self.ignore_extensions = getattr(self.config.ignore_extensions, "all_extensions")()
        self.ignore_files.append(str(output_file)) # 過去に出力したテキストを無視する必要がある


    def _should_ignore(self, path: Path) -> bool:
        """指定されたパスが無視対象かどうかを判定する"""
        if any(part in self.ignore_dirs for part in path.parts): return True # ディレクトリ名で無視
        if path.name in self.ignore_files: return True # ファイル名で無視        
        if path.suffix.lower() in self.ignore_extensions: return True # 拡張子で無視
            
        return False


    def _get_sorted_items(self, directory: Path) -> List[Path]:
        """指定されたディレクトリ内のアイテムを無視対象を除外してソートする. 内部メソッド"""
        # TODO: パーミッションエラーやディレクトリを見つけられなかった時のエラーハンドリングを追加する
        
        # ディレクトリ内のアイテムを取得し、無視対象を除外してソート
        filtered_items = [item for item in directory.iterdir() if not self._should_ignore(item)]
        items = sorted(
            filtered_items,
            key=lambda x: (x.is_file(), x.name.lower()) # ディレクトリを先に、次にファイル名でソート
        )
        return items
    

    def _generate_tree_recursive(
            self,
            current_path: Path,
            prefix: str = "",
            is_last: bool=True
    ) -> str:
        """ディレクトリ構造をtree形式で再帰的に生成する（内部メソッド）"""
        structure = ""
        connector = '└── ' if is_last else '├── '

        try:
            structure += f"{prefix}{connector}{current_path.name}\n"
            
            # ディレクトリの場合は再起的に呼び出す
            if current_path.is_dir():
                new_prefix = prefix + ('    ' if is_last else '│   ')
                # サブアイテムを取得する
                items = self._get_sorted_items(current_path)
                item_count = len(items)
                
                for i, item in enumerate(items):
                    is_last_item= (i == item_count - 1)
                    # 再帰的に呼び出す
                    structure += self._generate_tree_recursive(item, new_prefix, is_last_item)                    
        
        except OSError as e:
            structure += f"{prefix}{connector}[エラー: {e.strerror} ({current_path.name})]\n"
        except Exception as e:
            structure += f"{prefix}{connector}[予期せぬエラー: {e} ({current_path.name})]\n"

        return structure


    def generate_tree_structure(self)-> str:
        """ルートディレクトリから始まる全体のディレクt理構造の文字列を生成する"""
        structure = f"{self.root_path.name}\n"
        print(structure)

        # ルートディレクトリのアイテムを取得
        items = self._get_sorted_items(self.root_path)

        # 各アイテムに対して再起的に処理をする
        num_items = len(items)
        for i, item in enumerate(items):
            is_last_item = (i == num_items - 1)
            structure += self._generate_tree_recursive(item, "", is_last_item) # prefixは空文字列で初期化
        
        return structure
    

    def _format_file_content(self, file_path: Path) -> str:
        """単一のファイルのパスと内容を読み込み、整形して文字列で返す。 内部メソッド"""

        content_str = "" # 結果の文字列
        separator = "-" * 80 + "\n" # 区切り線の定義

        # 相対パスの取得
        relative_path = file_path.relative_to(self.root_path) # 相対パスを取得
        content_str += f"\n\n/{relative_path}:\n" # 相対パスを表示

        content_str += separator

        # ファイルの内容を読み込む
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines() # ファイルの全行をリストとして読み込む

            if not lines: # 空ファイルの場合
                content_str += " [空ファイル]\n"
            else:
                max_digits = len(str(len(lines))) # 行番号の桁数を計算。仮に20行であればmax_digitsは2になる。
                for i, line in enumerate(lines):
                    line_num_str = str(i+1).rjust(max_digits) # 行番号を右寄せで整形
                    content_str += f"{line_num_str} | {line.rstrip()}\n" # 行末の改行文字（rstrip()）を除去して、整形して追加
        except PermissionError:
            content_str += f" [エラー] ファイル '{file_path.name}' へのアクセス権がありません。\n"
        except OSError as e:
            content_str += f" [エラー] ファイル '{file_path.name}' 読み込み中にOSエラーが発生しました: {e.strerror}\n"
        except Exception as e:
            content_str += f" [エラー] ファイル '{file_path.name}' 読み込み中に予期せぬエラーが発生しました: {e}\n"
        
        content_str += separator # 最後に区切り線を追加
        return content_str


    def generate_file_contents(self)->str:
        """全ファイルのパスと内容を行番号付きで取得する"""
        contents=""

        files = [os.path.join(dirpath, f) for dirpath, _, filenames in os.walk(self.root_path) for f in filenames]
        files = [item for item in files if not self._should_ignore(Path(item))] # 無視対象を除外
        files = sorted(files, key=lambda x: (os.path.isfile(x), x.lower())) # ディレクトリを先に、次にファイル名でソート
        files = [Path(item) for item in files] # Pathオブジェクトに変換

        for file in files:
            contents += self._format_file_content(file)

        return contents
    

    def write_to_file(self, tree_structure: str, file_contents: str) -> None:
        """
        生成したディレクトリ構造とファイル内容を指定されたファイルに書き込む。

        Args:
            tree_structure (str): generate_tree_structureで生成された文字列。
            file_contents (str): generate_file_contentsで生成された文字列。
        """
        print(f"ファイル '{self.output_file}' に書き込み中...")
        try:
            # --- 出力ファイルの親ディレクトリが存在しない場合に作成 ---
            # self.output_path.parent は出力ファイルの親ディレクトリのPathオブジェクト
            # parents=True: 中間ディレクトリもまとめて作成 (例: /a/b/c.txt で a, b がなくても作る)
            # exist_ok=True: ディレクトリが既に存在していてもエラーにしない
            self.output_file.parent.mkdir(parents=True, exist_ok=True)

            # --- ファイルへの書き込み ---
            # 'w'モード: 書き込みモード。ファイルが存在すれば上書き、なければ新規作成。
            # encoding='utf-8': UTF-8エンコーディングで書き込む。
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write("--- ディレクトリ構造 ---\n")
                f.write(tree_structure)
                f.write("\n\n--- ファイル内容 ---\n") # 構造と内容の間に区切りを入れる
                f.write(file_contents)

            # 成功メッセージ (絶対パスで表示すると分かりやすい)
            print(f"ディレクトリリストが '{self.output_file.resolve()}' に出力されました。")

        except IOError as e:
            # ファイル書き込みに関するエラー (ディスクフル、アクセス権など)
            print(f"エラー: ファイル '{self.output_file}' に書き込めませんでした: {e}", file=sys.stderr)
        except Exception as e:
            # その他の予期せぬエラー
            print(f"予期せぬエラーが発生しました: {e}", file=sys.stderr)
    def run(self) -> None:
        """
        ディレクトリリスト化の全処理を実行する。
        """
        print(f"処理を開始します: {self.root_path}")
        try:
            # 1. ディレクトリ構造を生成
            tree_structure = self.generate_tree_structure()

            # 2. ファイル内容を生成
            file_contents = self.generate_file_contents()

            # 3. ファイルに書き込み
            self.write_to_file(tree_structure, file_contents)

            print("処理が正常に完了しました。")

        except Exception as e:
            # run の中で予期せぬエラーが起きた場合 (各メソッド内で捕捉されなかった場合など)
            print(f"\n処理中にエラーが発生しました: {e}", file=sys.stderr)
            # ここでプログラムを終了させるか、呼び出し元にエラーを伝えるかは設計による
            # 今回は呼び出し元 (mainブロック) で最終的なエラーハンドリングを行う想定
            raise # 捕捉したエラーを再度送出する


def test_should_ignore(lister: DirectoryLister) -> None:
    # テスト用のPathオブジェクトを作成 (Windows/Mac/Linuxで互換性のある書き方)
    test_path_git = Path(".git") / "config" # 相対パスで作成
    test_path_pycache = Path("my_module") / "__pycache__" / "cache_file.pyc"
    test_path_dsstore = Path("images") / ".DS_Store"
    test_path_log = Path("logs") / "app.log"
    test_path_normal_file = Path("src") / "main.py"
    test_path_normal_dir = Path("data")
    test_path_root_ignored_file = Path(".env")
    test_path_image = Path("assets") / "logo.png"

    print("-" * 20)
    print("無視判定テスト:")
    print(f"'{test_path_git}' は無視対象? -> {lister._should_ignore(test_path_git)}") # Trueのはず
    print(f"'{test_path_pycache}' は無視対象? -> {lister._should_ignore(test_path_pycache)}") # Trueのはず
    print(f"'{test_path_dsstore}' は無視対象? -> {lister._should_ignore(test_path_dsstore)}") # Trueのはず
    print(f"'{test_path_log}' は無視対象? -> {lister._should_ignore(test_path_log)}") # Trueのはず
    print(f"'{test_path_normal_file}' は無視対象? -> {lister._should_ignore(test_path_normal_file)}") # Falseのはず
    print(f"'{test_path_normal_dir}' は無視対象? -> {lister._should_ignore(test_path_normal_dir)}") # Falseのはず
    print(f"'{test_path_root_ignored_file}' は無視対象? -> {lister._should_ignore(test_path_root_ignored_file)}") # Trueのはず
    print(f"'{test_path_image}' は無視対象? -> {lister._should_ignore(test_path_image)}") # Trueのはず
    print("-" * 20)


def test_get_sorted_items() -> None:
    # テスト用のディレクトリとファイルを作成
    test_base_dir = Path("./temp_lister_test")
    test_base_dir.mkdir(exist_ok=True)
    (test_base_dir / "dir_a").mkdir(exist_ok=True)
    (test_base_dir / "file_z.txt").touch(exist_ok=True)
    (test_base_dir / "File_B.py").touch(exist_ok=True)
    (test_base_dir / "dir_c").mkdir(exist_ok=True)
    (test_base_dir / ".env").touch(exist_ok=True) # 無視されるファイル
    (test_base_dir / "image.png").touch(exist_ok=True) # 無視される拡張子
    (test_base_dir / ".git").mkdir(exist_ok=True) # 無視されるディレクトリ

    # Listerインスタンスを作成 (テストディレクトリを対象)
    lister = DirectoryLister(
        Path(test_base_dir),
        Path("./output.txt"),
        config=get_config(Path('./settings.yml'))
    )

    print(f"\n'{test_base_dir}' 内のソート済みアイテム:")
    sorted_items = lister._get_sorted_items(test_base_dir)
    if not sorted_items:
        print("  (アイテムが見つからないか、アクセスエラー)")
    for item in sorted_items:
        item_type = "Dir " if item.is_dir() else "File"
        print(f"  {item_type}: {item.name}")

    # 期待される出力順序の確認 (手動)
    # dir_a, dir_c, File_B.py, file_z.txt の順になるはず


def main() -> None:
    # インスタンス化
    lister = DirectoryLister(
        directory_path=Path('./'),
        output_file=Path('text.txt'),
        config=get_config(Path('./settings.yml'))
    )

    # ディレクトリリスト化を実行
    lister.run()


    # for item in a:
    #     print(item)

    # test_should_ignore(lister)
    # test_get_sorted_items()


if __name__ == "__main__":
    main()