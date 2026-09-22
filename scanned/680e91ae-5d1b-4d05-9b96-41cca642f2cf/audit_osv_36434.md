# [M] Blinko: Unauthorized Arbitrary File Read - /api/file/temp

## Summary
Severity: Medium
Advisory: CVE-2026-23482
Aliases: GHSA-hrwx-rhrx-f9mm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/CVE-2026-23482
Type: osv

## Details
Blinko is an AI-powered card note-taking project. Prior to version 1.8.4, the file server endpoint does not perform permission checks on the temp/ path and does not filter path traversal sequences, allowing unauthorized attackers to read arbitrary files on the server. When scheduled backup tasks are enabled, attackers can read backup files to obtain all user notes and user TOKENS. This issue has been patched in version 1.8.4.

## References
- https://github.com/blinkospace/blinko/releases/tag/1.8.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23482.json
- https://github.com/blinkospace/blinko/security/advisories/GHSA-hrwx-rhrx-f9mm
- https://nvd.nist.gov/vuln/detail/CVE-2026-23482
- https://github.com/blinkospace/blinko/commit/c48851090767feba431418630c495d90a7da1781
