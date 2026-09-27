# [C] rAthena has heap-based buffer overflow in login server

## Summary
Severity: Critical
Advisory: CVE-2025-58447
Aliases: GHSA-4p33-6xqr-cm6x
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-09
Source: https://osv.dev/vulnerability/CVE-2025-58447
Type: osv

## Details
rAthena is an open-source cross-platform massively multiplayer online role playing game (MMORPG) server. Versions prior to commit 2f5248b have a heap-based buffer overflow in the login server, remote attacker to overwrite adjacent session fields by sending a crafted `CA_SSO_LOGIN_REQ` with an oversized token length. This leads to immediate denial of service (crash) and it is possible to achieve remote code execution via heap corruption. Commit 2f5248b fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58447.json
- https://github.com/rathena/rathena/security/advisories/GHSA-4p33-6xqr-cm6x
- https://nvd.nist.gov/vuln/detail/CVE-2025-58447
- https://github.com/rathena/rathena/commit/2f5248b9cd9a8c6b42422ddecfc4cc2cd0e69e4b
