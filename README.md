# Decky Web Links

Decky Web Links is a community preset catalog for web applications that can be
launched from a Decky plugin. Each preset describes the application, its URL,
recommended browser, and browser launch flags. The files in `presets/` are the
editable source of truth; `dist/manifest.json` is the combined file intended
for consumers such as the plugin frontend.

This repository contains the catalog and its publishing automation. It does
not contain the Decky plugin itself.

## Repository layout

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── SUBMIT_PRESET.yml   # GitHub form for suggesting a preset
│   └── workflows/
│       └── build-manifest.yml # Rebuilds the manifest on main
├── presets/
│   └── <preset-id>/
│       ├── preset.json        # One preset's metadata
│       └── art/               # Optional local artwork files
├── scripts/
│   └── build_manifest.py      # Compiles preset files into the manifest
└── dist/
    └── manifest.json          # Generated community catalog
```

Each preset belongs in its own directory, named with its stable, URL-friendly
ID—for example, `presets/amazon-luna/preset.json`.

## Submitting a preset

### Community submissions

1. Open the repository's **Issues** tab on GitHub and choose **Submit Web App
   Preset** (the form is defined in
   `.github/ISSUE_TEMPLATE/SUBMIT_PRESET.yml`).
2. Provide the application's title, category, launch URL, recommended browser,
   launch flags, controller template, and any artwork URLs that are available.
3. Submit the issue. A maintainer reviews the details, tests the preset as
   appropriate, and can request clarification or changes.

An issue is a proposal, not a catalog change. The form does not create
`preset.json`, download artwork, or update the manifest automatically.
Maintainers add accepted presets to the repository, normally through a pull
request, so changes can be reviewed before publication.

Please submit a URL for the actual web application and include only launch
flags needed for it to work. Artwork URLs should point to usable image files.
The form suggests these image sizes: cover `600x900`, grid `920x430`, hero
`3840x1240`, and icon `256x256`; the form also accepts a PNG logo. The compiler
does not check image dimensions or download files from those URLs.

### Adding a preset in a pull request

Create a directory under `presets/` and add a UTF-8 JSON file named
`preset.json`. The following fields are required by the current compiler:

| Field | Purpose | Example |
| --- | --- | --- |
| `id` | Stable preset identifier | `"amazon-luna"` |
| `title` | Display name | `"Amazon Luna"` |
| `category` | Catalog category | `"Game Streaming"` |
| `url` | Web application URL | `"https://luna.amazon.com"` |
| `recommended_browser` | Browser package identifier | `"com.google.Chrome"` |
| `launch_flags` | Browser command-line arguments | `"--kiosk --app=\"https://luna.amazon.com\""` |

Other useful metadata used by existing entries includes `controller_template`,
`author`, and `steamgriddb_search_term`. The compiler preserves these extra
fields from `preset.json`.

Example:

```json
{
  "id": "example-app",
  "title": "Example App",
  "category": "Productivity",
  "url": "https://example.com",
  "recommended_browser": "com.google.Chrome",
  "launch_flags": "--kiosk --app=\"https://example.com\"",
  "controller_template": "trackpad_mouse",
  "author": "YourName",
  "steamgriddb_search_term": "Example App"
}
```

Keep the `id` stable after publication and use the same value for the preset
directory name. Use valid JSON (double quotes around property names and string
values; no trailing commas).

### Artwork files

The compiler looks for artwork files in the preset's `art/` directory, using
these names:

| Type | Supported file names |
| --- | --- |
| Cover | `cover.png`, `cover.jpg`, `cover.jpeg` |
| Grid | `grid.png`, `grid.jpg`, `grid.jpeg` |
| Hero | `hero.png`, `hero.jpg`, `hero.jpeg` |
| Logo | `logo.png`, `logo.jpg`, `logo.jpeg` |
| Icon | `icon.png`, `icon.jpg`, `icon.jpeg` |

For example, `presets/example-app/art/grid.png` is included in the compiled
manifest as a repository-relative path. Only the first matching extension in
the order shown by the compiler (`png`, `jpg`, then `jpeg`) is selected for
each artwork type. If there are no matching files, the compiled preset has an
empty `artwork` object. Artwork URLs entered in an issue need to be reviewed
and, if accepted, added as files before the compiler can include them.

## Building the manifest

The builder uses only Python's standard library. Python 3.12 is the version
used by the GitHub Actions workflow.

From the repository root, run:

```sh
python scripts/build_manifest.py
```

On Windows, if `python` is not available on `PATH`, use the Python launcher:

```powershell
py -3.12 scripts\build_manifest.py
```

The script scans `presets/*/preset.json` in sorted order, parses each file,
checks that the six required fields are present, adds artwork paths found in
each preset's `art/` directory, and writes the combined JSON to
`dist/manifest.json`. The output contains a manifest `version`, a
`total_presets` count, and a `presets` array.

The generated manifest is a build artifact, but it is intentionally tracked
in Git and should be committed when it changes. Do not edit it as the only
change for a preset: update the corresponding source JSON and rebuild it.

### Current compiler behavior to be aware of

- The compiler currently checks for required fields, but does not validate
  their types, URL format, uniqueness, category values, or artwork dimensions.
- A malformed preset or one missing a required field is reported and skipped.
  The current script still writes a manifest and does not return a failing
  process status for those errors. Review its output and inspect the generated
  manifest when building locally.
- Artwork in the generated manifest is constructed from files in the local
  `art/` directory. An `artwork` value already present in `preset.json` is
  replaced by the files found there.
- The compiler currently sets the output version to `1.0.0`; it does not carry
  forward other top-level metadata from an existing manifest.

These are descriptions of the current script, not guarantees of broader
validation.

## Automated build and publishing

The workflow in `.github/workflows/build-manifest.yml` runs on:

- Pushes to the `main` branch that change files under `presets/`, `scripts/`,
  or the workflow itself.
- A manual **workflow_dispatch** run from the GitHub Actions tab.

After checking out the repository, the workflow sets up Python 3.12, runs
`python scripts/build_manifest.py`, and commits a changed
`dist/manifest.json` using the `stefanzweifel/git-auto-commit-action` action.
The commit uses the message `chrono: auto-generate manifest.json [skip ci]`.
The workflow declares `contents: write` permission so the action can push the
generated update.

In the normal contribution flow, merge a preset pull request into `main`. The
resulting push triggers the workflow when it includes a matching path. Check
the Actions run and the generated manifest after the workflow completes. A
manual run is available if a build needs to be repeated.

The workflow uses the repository's default branch named `main`. If publishing
does not work, confirm that GitHub Actions is enabled and allowed to write
repository contents under the repository's Actions settings.

## Consuming the manifest

The generated manifest is available as a raw GitHub file. A plugin frontend
can fetch it with a URL of this form:

```ts
const MANIFEST_URL =
  "https://raw.githubusercontent.com/<GITHUB_OWNER>/decky-web-links/main/dist/manifest.json";
```

Replace `<GITHUB_OWNER>` with the account or organization that owns the
repository. For a public repository, the raw URL can be fetched without
authentication. Update the plugin's fetch code separately; this repository
does not include that plugin frontend.

## License and contributions

Please follow the repository's license and contribution guidance when
submitting presets or artwork. If no license or contribution policy has been
added yet, clarify those terms before accepting community-provided material.
