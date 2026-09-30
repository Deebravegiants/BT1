# [M] Docmost has cross-page attachment overwrite via flawed attachmentId overwrite validation

## Summary
Severity: Medium
Advisory: CVE-2026-34213
Aliases: GHSA-89fp-2hch-j9gp
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-34213
Type: osv

## Details
Docmost is open-source collaborative wiki and documentation software. Starting in version 0.3.0 and prior to version 0.71.0, improper authorization in Docmost allows a low-privileged authenticated user to overwrite another page's attachment within the same workspace by supplying a victim `attachmentId` to `POST /api/files/upload`. This is a remote integrity issue requiring no victim interaction. Version 0.71.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34213.json
- https://github.com/docmost/docmost/security/advisories/GHSA-89fp-2hch-j9gp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34213
