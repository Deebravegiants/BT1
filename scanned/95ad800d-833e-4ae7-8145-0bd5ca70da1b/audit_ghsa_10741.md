# [M] NiceGUI: Upload filename sanitization bypass via backslashes allows path traversal on Windows

## Summary
Severity: Medium
Advisory: GHSA-w8wv-vfpc-hw2w
CVE: CVE-2026-39844
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-w8wv-vfpc-hw2w
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=0 <3.10.0

## Details
### Summary

The upload filename sanitization introduced in GHSA-9ffm-fxg3-xrhh uses `PurePosixPath(filename).name` to strip path components. Since `PurePosixPath` only recognizes forward slashes (`/`) as path separators, an attacker can bypass this sanitization on Windows by using backslashes (`\`) in the upload filename.

Applications that construct file paths using `file.name` (a pattern demonstrated in NiceGUI's bundled examples) are vulnerable to arbitrary file write on Windows.

### Details

The sanitization in `nicegui/elements/upload_files.py` uses:

```python
filename = PurePosixPath(upload.filename or '').name
```

`PurePosixPath` treats backslashes as literal characters, not path separators:

```python
>>> PurePosixPath('..\\..\\secret\\evil.txt').name
'..\\..\\secret\\evil.txt'  # Not stripped!
```

When this filename is used in a path operation on Windows (e.g., `Path('uploads') / file.name`), Windows `Path` interprets backslashes as directory separators, resolving the path outside the intended directory.

### Impact

On Windows deployments of NiceGUI applications that use `file.name` in path construction:

- **Arbitrary file write** outside the intended upload directory
- **Potential remote code execution** through overwriting application files or placing executables in known locations
- **Data integrity loss** through overwriting existing files

Linux and macOS are not affected, as they treat backslashes as literal filename characters.

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-w8wv-vfpc-hw2w
- https://nvd.nist.gov/vuln/detail/CVE-2026-39844
- https://github.com/zauberzeug/nicegui/commit/d38a702e3af2da5b0708f689be8d71413fc77056
- https://github.com/zauberzeug/nicegui
- https://github.com/zauberzeug/nicegui/releases/tag/v3.10.0
