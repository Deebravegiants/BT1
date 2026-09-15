# [H] Quicly: Remote Denial of Service via assertion failure when CRYPTO stream handshake data exceeds 32KB

## Summary
Severity: High
Advisory: CVE-2026-44435
Aliases: GHSA-2cw9-5673-73gv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-44435
Type: osv

## Details
Quicly is an IETF QUIC protocol implementation intended primarily for use within the H2O HTTP server. Prior to commit 937d0e9, an assertion failure is raised when the total number of valid handshake messages received over a CRYPTO stream of a single packet number space exceeds 32KB, causing a Denial of Service. This issue has been fixed by commit 937d0e9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44435.json
- https://github.com/h2o/quicly/security/advisories/GHSA-2cw9-5673-73gv
- https://nvd.nist.gov/vuln/detail/CVE-2026-44435
- https://github.com/h2o/quicly/commit/937d0e9e7c669fc2bee4920632ab6aaac60e4d81
