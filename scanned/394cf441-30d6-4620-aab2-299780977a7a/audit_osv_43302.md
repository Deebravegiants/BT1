# [M] Ente: 2of3 cards v1 contain a checksum that enables offline guessing of low-entropy secrets

## Summary
Severity: Medium
Advisory: CVE-2026-73230
Aliases: GHSA-v6x7-rrch-9q9w
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73230
Type: osv

## Details
Ente provides end-to-end encrypted cloud services and security tools. Prior to 2026.07.28, Ente 2of3 card format version 1 stored the secret byte length and 32-bit FNV-1a checksum in cleartext on every card, allowing someone with one card to test candidate secrets offline and recover low-entropy or predictable secrets. This issue is fixed in version 2026.07.28.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73230.json
- https://github.com/ente/ente/security/advisories/GHSA-v6x7-rrch-9q9w
- https://nvd.nist.gov/vuln/detail/CVE-2026-73230
- https://github.com/ente/ente/commit/6681d8370a37c2fc745d3098126ba1ee62bf06a5
- https://github.com/ente/ente/commit/c3d2e400ae6fa66d5ce7df422136d28805fe1442
- https://github.com/ente/ente/pull/11729
