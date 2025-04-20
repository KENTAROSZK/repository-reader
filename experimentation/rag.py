import sys
import os

from pathlib import Path

# パスを追加（絶対パス or 相対パス）
sys.path.append(os.path.abspath("../project_module/src/project_module"))


# 自作モジュールをインポート
from directory_lister.directory_lister import DirectoryLister
from directory_lister.ignore_config import get_config, IgnoreConfig



def main() -> None:
    # 検索を開始するディレクトリのパスを指定
    ROOT_DIR = Path(__file__).resolve().parents[1] # 2つ上のディレクトリを取得する
    # 設定ファイルのパスを指定
    SETTING_YML_DIR = Path(__file__).resolve().parent.parent/ "project_module/src/project_module/directory_lister" / 'settings.yml'

    # インスタンス化
    lister = DirectoryLister(
        directory_path=Path(ROOT_DIR),
        output_file=Path('./text.txt'),
        config=get_config(Path(SETTING_YML_DIR))
    )

    # ディレクトリリスト化を実行
    lister.run()


if __name__ == "__main__":
    main()