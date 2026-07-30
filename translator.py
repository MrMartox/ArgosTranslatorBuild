#!/usr/bin/env python3

import json
import sys

import argostranslate.package
import argostranslate.translate


def update_packages():
    print("Updating package list...")
    argostranslate.package.update_package_index()
    print("Package list updated.")


def install_package(package_name):
    print("Updating package index...")
    argostranslate.package.update_package_index()

    available_packages = argostranslate.package.get_available_packages()

    try:
        from_code, to_code = package_name.split("-")[1].split("_")
    except ValueError:
        print(f"Error: Invalid package name '{package_name}'.")
        return

    package = next(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code,
            available_packages,
        ),
        None,
    )

    if package is None:
        print("Package not found.")
        return

    argostranslate.package.install_from_path(package.download())
    print("Installed.")


def translate_text(source, target, text):
    return argostranslate.translate.translate(text, source, target)


def runtime():
    """
    Reads one JSON object per line from stdin.

    Request:
    {
        "from": "en",
        "to": "de",
        "text": "Hello World"
    }

    Response:
    {
        "success": true,
        "translation": "Hallo Welt"
    }
    """

    print(json.dumps({"ready": True}), flush=True)

    while True:
        line = sys.stdin.readline()

        if not line:
            break

        line = line.strip()

        if not line:
            continue

        try:
            request = json.loads(line)

            if request.get("cmd") == "exit":
                print(json.dumps({"success": True}), flush=True)
                break

            source = request["from"]
            target = request["to"]
            text = request["text"]

            translated = translate_text(source, target, text)

            print(
                json.dumps(
                    {
                        "success": True,
                        "translation": translated,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

        except Exception as e:
            print(
                json.dumps(
                    {
                        "success": False,
                        "error": str(e),
                    }
                ),
                flush=True,
            )


def print_help():
    print("""
Usage:

program.py update
program.py install translate-en_de
program.py runtime
program.py --from en --to de "Hello"
""")


def main():
    args = sys.argv[1:]

    if not args:
        print_help()
        return

    if args[0] == "runtime":
        runtime()
        return

    if args[0] == "update":
        update_packages()
        return

    if args[0] == "install":
        install_package(args[1])
        return

    if "--from" in args and "--to" in args:
        source = args[args.index("--from") + 1]
        target = args[args.index("--to") + 1]

        text = " ".join(
            arg
            for i, arg in enumerate(args)
            if i
            not in (
                args.index("--from"),
                args.index("--from") + 1,
                args.index("--to"),
                args.index("--to") + 1,
            )
        )

        print(translate_text(source, target, text))
        return

    print_help()


if __name__ == "__main__":
    main()