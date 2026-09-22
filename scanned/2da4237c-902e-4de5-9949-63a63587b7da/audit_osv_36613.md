# [H] ConvertX Vulnerable to Arbitrary File Deletion via Path Traversal in `POST /delete`

## Summary
Severity: High
Advisory: CVE-2026-24741
Aliases: GHSA-w372-w6cr-45jp
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24741
Type: osv

## Details
ConvertXis a self-hosted online file converter. In versions prior to 0.17.0, the `POST /delete` endpoint uses a user-controlled `filename` value to construct a filesystem path and deletes it via `unlink` without sufficient validation. By supplying path traversal sequences (e.g., `../`), an attacker can delete arbitrary files outside the intended uploads directory, limited only by the permissions of the server process. Version 0.17.0 fixes the issue.

## References
- https://github.com/C4illin/ConvertX/security/advisories/GHSA-w372-w6cr-45jp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24741.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24741
- https://github.com/C4illin/ConvertX/commit/7a936bdc0463936463616381ca257b13babc5e77
