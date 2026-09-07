# [M]  Werkzeug safe_join() allows Windows special device names with compound extensions

## Summary
Severity: Medium
Advisory: GHSA-87hc-h4r5-73f7
CVE: CVE-2026-21860
CWE: CWE-67
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-87hc-h4r5-73f7
Type: github-advisory

## Affected
- PyPI: `Werkzeug` — affected >=0 <3.1.5

## Details
Werkzeug's `safe_join` function allows path segments with Windows device names that have file extensions or trailing spaces. On Windows, there are special device names such as `CON`, `AUX`, etc that are implicitly present and readable in every directory. Windows still accepts them with any file extension, such as `CON.txt`, or trailing spaces such as `CON `.

This was previously reported as https://github.com/pallets/werkzeug/security/advisories/GHSA-hgf8-39gv-g3f2, but the fix failed to account for compound extensions such as `CON.txt.html` or trailing spaces. It also missed some additional special names.

`send_from_directory` uses `safe_join` to safely serve files at user-specified paths under a directory. If the application is running on Windows, and the requested path ends with a special device name, the file will be opened successfully, but reading will hang indefinitely.

## References
- https://github.com/pallets/werkzeug/security/advisories/GHSA-87hc-h4r5-73f7
- https://nvd.nist.gov/vuln/detail/CVE-2026-21860
- https://github.com/pallets/werkzeug/commit/7ae1d254e04a0c33e241ac1cca4783ce6c875ca3
- https://github.com/pallets/werkzeug
