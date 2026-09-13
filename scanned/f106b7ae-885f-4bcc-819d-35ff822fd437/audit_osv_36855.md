# [M] Zulip: Path Traversal in Import

## Summary
Severity: Medium
Advisory: CVE-2026-26058
Aliases: GHSA-xm5c-c6mp-3956
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-26058
Type: osv

## Details
Zulip is an open-source team collaboration tool. From version 1.4.0 to before version 11.6, ./manage.py import reads arbitrary files from the server filesystem via path traversal in uploads/records.json. A crafted export tarball causes the server to copy any file the zulip user can read into the uploads directory during import. This issue has been patched in version 11.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26058.json
- https://github.com/zulip/zulip/security/advisories/GHSA-xm5c-c6mp-3956
- https://nvd.nist.gov/vuln/detail/CVE-2026-26058
- https://github.com/zulip/zulip/commit/2df49e7750ce3fc49ef1d44b1c4ece654d4b754c
