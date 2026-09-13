# [M] PocketMine-MP before 5.43.1 Denial of Service via unauthenticated login

## Summary
Severity: Medium
Advisory: CVE-2026-86199
Aliases: GHSA-g2fj-p69p-9chp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86199
Type: osv

## Details
PocketMine-MP versions before 5.43.1 fail to properly validate the Certificate field during offline login authentication. Unauthenticated players can trigger an uninitialized property access error that crashes the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86199.json
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-g2fj-p69p-9chp
- https://nvd.nist.gov/vuln/detail/CVE-2026-86199
- https://www.vulncheck.com/advisories/pocketmine-mp-before-5.43.1-denial-of-service-via-unauthenticated-login
- https://github.com/pmmp/PocketMine-MP/commit/8c75a1d739e8e190d3cc2338b25cebcc9c052b1b
- https://github.com/pmmp/PocketMine-MP/commit/e4aaef4ee0f769b52dc0347a1d6da403b9691115
