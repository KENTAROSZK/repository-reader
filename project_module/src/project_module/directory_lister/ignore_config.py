import yaml
from pydantic import BaseModel
from typing import List
from pathlib import Path

class IgnoreExtensionsConfig(BaseModel):
    images: List[str] | None
    videos: List[str] | None
    compressed: List[str] | None
    binaries: List[str] | None
    documents: List[str] | None
    others: List[str] | None

    def all_extensions(self) -> List[str]:
        """全ての拡張子を取得する"""
        all_exts = []
        for attr in self.__dict__.values():
            if isinstance(attr, list):
                all_exts.extend(attr)
        return all_exts



class IgnoreConfig(BaseModel):
    ignore_dirs: List[str] | None
    ignore_files: List[str] | None
    ignore_extensions: IgnoreExtensionsConfig | None


def get_config(settings_yaml_path: Path)->IgnoreConfig:
    with open(settings_yaml_path, 'rb') as f:
        yml = yaml.safe_load(f)
    
    return IgnoreConfig.model_validate(yml)


def main() -> None:
    settings_yaml_path = Path('./ignore_settings.yml')
    config = get_config(settings_yaml_path)

    print()
    print(f"{getattr(config, 'ignore_dirs')=}")
    print()
    print(f"{getattr(config, 'ignore_extensions')=}")
    print()
    print(f"{getattr(config.ignore_extensions, 'images')=}")
    print()
    print(config.ignore_extensions.all_extensions())
    print()


if __name__ == "__main__":
    main()