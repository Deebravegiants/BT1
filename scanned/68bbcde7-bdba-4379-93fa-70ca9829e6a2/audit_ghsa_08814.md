# [M] Regression in pymdownx.snippets reintroduces sibling-prefix path traversal bypass despite restrict_base_path

## Summary
Severity: Medium
Advisory: GHSA-62q4-447f-wv8h
CVE: CVE-2026-46338
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-62q4-447f-wv8h
Type: github-advisory

## Affected
- PyPI: `pymdown-extensions` — affected >=10.0.1 <10.21.3

## Details
# Summary

`pymdownx.snippets` has a regression of the CVE-2023-32309 / GHSA-jh85-wwv9-24hv fix. With `restrict_base_path: True` (the default), the current `filename.startswith(base)` containment check does not enforce a directory boundary. As a result, a markdown snippet directive can read files from sibling paths that share the same prefix as `base_path`, such as `docs` vs `docs_internal`.

The regression was introduced in PR #2039 / commit `7c13bda5b7793b172efd1abb6712e156a83fe07d`, which replaced the original directory-identity check with a plain string-prefix comparison.

# Details

The regression was introduced in commit `7c13bda5b7793b172efd1abb6712e156a83fe07d` (2023-05-15, #2039 *"Fix regression of snippets nested deeply under specified base path"*), which relaxed the original `os.path.samefile(base, os.path.dirname(filename))` check to a plain `startswith(base)`.

`SnippetPreprocessor.get_snippet_path()` in `pymdownx/snippets.py`:

```python
if self.restrict_base_path:
    filename = os.path.abspath(os.path.join(base, path))
    # If the absolute path is no longer under the specified base path, reject the file
    if not filename.startswith(base):
        continue
```

`base` is `os.path.abspath(b)` and has no trailing separator. `str.startswith(base)` is `True` for any `filename` whose string representation begins with the same characters as `base`, regardless of whether those characters end at a directory boundary.

Concrete example:

* `base = "/x/docs"`
* `path = "../docs_secret/leak.txt"` (inside the markdown snippet directive)
* `os.path.join(base, path)` → `"/x/docs/../docs_secret/leak.txt"`
* `os.path.abspath(...)`     → `"/x/docs_secret/leak.txt"`
* `filename.startswith(base)` → `True`, because `"/x/docs_secret/..."` begins with the literal string `"/x/docs"`.

All releases from **10.0.1 (2023-05-15) through 10.21.2 (current)** are affected.

# Impact

Arbitrary file read within the host the build runs on, bounded by the prefix match. With `base_path = /x/docs` the attacker can read files from any sibling directory whose path begins with the literal string `/x/docs` followed by any non-separator character — for example `/x/docs_internal/`, `/x/docs.bak/`, `/x/docs2/`.

The threat model is the same as the original CVE-2023-32309: markdown content processed by the snippets preprocessor in a build pipeline (typical scenario: an MkDocs documentation site built in CI from PR contributions or otherwise less-trusted markdown) can read files outside the configured base. CI builds that publish the generated HTML expose the read file to the public; CI builds with secrets on disk leak those secrets.

# Reproduction

Minimal local PoC, non-destructive:

```python
import os, shutil, tempfile, markdown

work = tempfile.mkdtemp(prefix="pmx_poc_")
try:
    base    = os.path.join(work, "docs")
    sibling = os.path.join(work, "docs_secret")
    os.makedirs(base)
    os.makedirs(sibling)
    with open(os.path.join(sibling, "leak.txt"), "w") as f:
        f.write("TOP_SECRET_FROM_SIBLING_DIR\n")

    out = markdown.markdown(
        '--8<-- "../docs_secret/leak.txt"\n',
        extensions=["pymdownx.snippets"],
        extension_configs={
            "pymdownx.snippets": {
                "base_path": [base],
                "restrict_base_path": True,
                "check_paths": True,
            }
        },
    )
    print(out)  # -> <p>TOP_SECRET_FROM_SIBLING_DIR</p>
finally:
    shutil.rmtree(work)
```

Default `restrict_base_path: True` is sufficient — no non-default option is required.

# Suggested fix

Minimal change — require the separator after the base prefix:

```diff
-                        if not filename.startswith(base):
+                        # Append `os.sep` so a sibling directory whose name shares a prefix
+                        # (e.g. `/x/docs` vs `/x/docs_evil`) cannot satisfy the check.
+                        if not filename.startswith(base + os.sep):
                             continue
```

This preserves the original intent (allow snippets nested at any depth under `base_path`) while restoring the directory-boundary check. It does not affect the `os.path.isdir(base)` branch where `base` is a file (that branch still uses `os.path.samefile`).

Alternative: `os.path.commonpath([base, filename]) == base` is equivalent and slightly more idiomatic, though it raises `ValueError` on different drives on Windows and would need a `try/except`. The `startswith(base + os.sep)` fix is the smaller diff.

Note: this fix does not change behaviour for symlinks inside `base_path`. The existing implementation uses `os.path.abspath` (not `os.path.realpath`), so a symlink within `base_path` pointing outside is still followed. That is a separate concern — symlinks require write access to `base_path`, a much higher bar than the current bypass — and matches the behaviour the CVE-2023 fix established.

# Regression test

A regression test class `TestSnippetsSiblingPrefix` was added in `tests/test_extensions/test_snippets.py`. It uses `tests/test_extensions/_snippets/nested` as `base_path` and a new fixture directory `tests/test_extensions/_snippets/nested_sibling_evil/leak.txt`. It asserts that the markdown directive `--8<-- "../nested_sibling_evil/leak.txt"` raises `SnippetMissingError`.

* Without fix: test fails (`AssertionError: SnippetMissingError not raised`, sibling file is silently read).
* With fix: test passes.

Full suite: `python -m pytest tests/ -q` → **738 passed** (737 baseline + 1 new regression test). No regressions.

# Affected versions

`>= 10.0.1, <= 10.21.2`

## References
- https://github.com/facelessuser/pymdown-extensions/security/advisories/GHSA-62q4-447f-wv8h
- https://github.com/facelessuser/pymdown-extensions/pull/2039
- https://github.com/facelessuser/pymdown-extensions
