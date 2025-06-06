import json

# TOKEN = os.environ.get("CATEGORY_TOKEN")

PACKER_ACTION_CONTENT = """name: packer

on:
  workflow_dispatch:

jobs:
  pack:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Checkout category repo
        uses: actions/checkout@v4
        with: 
          repository: freeze-dolphin/fragments-category
          path: fragments-category
          ref: master
          token: ${{ secrets.CATEGORY_TOKEN }}

      - name: Upload metadata
        uses: actions/upload-artifact@v4
        with:
          name: metadata
          path: |
            fragments-category/songs/songlist
            fragments-category/songs/packlist
            fragments-category/songs/unlocks
          overwrite: true"""

PACKER_ARCPKG_ACTION_CONTENT = """name: packer-arcpkg

on:
  workflow_dispatch:

jobs:
  pack_arcpkg:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Checkout category repo
        uses: actions/checkout@v4
        with: 
          repository: freeze-dolphin/fragments-category
          path: fragments-category
          ref: master
          token: ${{ secrets.CATEGORY_TOKEN }}
          
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
          
      - run: python scripts/generate_arcpkgs.py"""


def song(song_id: str) -> str:
    return f"""
      - name: Upload artifact '{song_id}'
        uses: actions/upload-artifact@v4
        with:
          name: {song_id}
          path: fragments-category/songs/{song_id}
          overwrite: true"""


def song_arcpkg(song_id: str) -> str:
    return f"""
      - name: Upload artifact '{song_id}'
        uses: actions/upload-artifact@v4
        with:
          name: {song_id}
          path: arcpkgs/lowiro.{song_id}.arcpkg
          overwrite: true"""


if __name__ == "__main__":
    with open("fragments-category/songs/songlist", "r", encoding="utf-8") as songlist_f:
        songlist = json.loads(songlist_f.read())["songs"]

    with open(
        "fragments-category/songs/songlist_aprilfools", "r", encoding="utf-8"
    ) as songlist_f:
        songlist += json.loads(songlist_f.read())["songs"]

    for song_info in songlist:
        if "deleted" in song_info and song_info["deleted"]:
            continue

        song_id = song_info["id"]

        PACKER_ACTION_CONTENT += song(song_id)
        PACKER_ARCPKG_ACTION_CONTENT += song_arcpkg(song_id)
        print(f"- {song_id}")

    with open(".github/workflows/packer.yml", "w") as packer_f:
        packer_f.write(PACKER_ACTION_CONTENT)

    with open(".github/workflows/packer_arcpkg.yml", "w") as packer_arcpkg_f:
        packer_arcpkg_f.write(PACKER_ARCPKG_ACTION_CONTENT)
