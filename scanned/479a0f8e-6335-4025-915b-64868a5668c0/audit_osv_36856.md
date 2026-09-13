# [C] calibre: Path Traversal Vulnerability Enables Arbitrary File Write and Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-26064
Aliases: GHSA-72ch-3hqc-pgmp
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-26064
Type: osv

## Details
calibre is a cross-platform e-book manager for viewing, converting, editing, and cataloging e-books. Versions 9.2.1 and below contain a Path Traversal vulnerability that allows arbitrary file writes anywhere the user has write permissions. On Windows, this leads to Remote Code Execution by writing a payload to the Startup folder, which executes on next login. Function extract_pictures only checks startswith('Pictures'), and does not sanitize '..' sequences. calibre's own ZipFile.extractall() in utils/zipfile.py does sanitize '..' via _get_targetpath(), but extract_pictures() bypasses this by using manual zf.read() + open(). This issue has been fixed in version 9.3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26064.json
- https://github.com/kovidgoyal/calibre/security/advisories/GHSA-72ch-3hqc-pgmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-26064
- https://github.com/kovidgoyal/calibre/commit/e1b5f9b45a5e8fa96c136963ad9a1d35e6adac62
