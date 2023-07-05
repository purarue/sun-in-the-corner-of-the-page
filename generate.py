#!/usr/bin/env python3

from pathlib import Path

this_dir = Path(__file__).parent
data_dir = this_dir / "images"
data_file = this_dir / "data.yaml"

import click
from yattag.doc import Doc
from yaml import safe_load, safe_dump


@click.command()
@click.argument("COPY_TO", default="build")
def generate(copy_to: str) -> None:
    doc, tag, text = Doc().tagtext()

    metadata = safe_load(data_file.read_text())

    doc.asis("<!DOCTYPE html>")
    # force light theme
    with tag("html", ("data-theme", "light"), lang="en"):
        with tag("head"):
            doc.stag("meta", charset="utf-8")
            doc.stag(
                "meta", name="viewport", content="width=device-width, initial-scale=1"
            )
            doc.stag(
                "link",
                rel="stylesheet",
                href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css",
            )
            # css
            with tag("style"):
                # ligt blue background color
                text(
                    """html,body {background-color: #e6f1ff;}
body {margin: 0;}
img {max-height: 90vh; display: block; margin-left: auto; margin-right: auto; }
footer { text-align: center; }"""
                )
            with tag("title"):
                text("Suns in the Corner of the Page")

        with tag("body"):
            with tag("div", klass="container"):
                for file in sorted(data_dir.iterdir(), reverse=True):
                    if file.suffix not in {".jpg", ".png"}:
                        print(f"Skipping {file.name}")
                        continue
                    print(f"Generated {file.name} card")
                    with tag("article"):
                        with tag("a", href=f"images/{file.name}", target="_blank"):
                            doc.stag("img", src=f"images/{file.name}", alt=file.name)
                        with tag("footer"):
                            try:
                                text(metadata[file.name]["text"])
                            except (KeyError, TypeError):
                                print(f"Missing metadata for {file.name}")
                                # write to yaml file
                                metadata[file.name] = {
                                    "text": input(
                                        f"Enter text for {file.name}: "
                                    ).strip()
                                }
                                data_file.write_text(safe_dump(metadata))
                                raise

    # write to file
    output_file = this_dir / "index.html"
    output_file.write_text(doc.getvalue())

    # copy to destination
    import shutil

    target = Path(copy_to)
    if not target.exists():
        target.mkdir(parents=True)

    assert target.is_dir()
    shutil.copy(output_file, target)
    shutil.copytree(data_dir, target / "images", dirs_exist_ok=True)


if __name__ == "__main__":
    generate()
