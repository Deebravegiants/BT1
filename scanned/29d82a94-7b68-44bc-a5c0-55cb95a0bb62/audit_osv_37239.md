# [M] Path Traversal in Coppermine Photo Gallery

## Summary
Severity: Medium
Advisory: CVE-2026-3013
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-3013
Type: osv

## Details
Coppermine Photo Gallery in versions 1.6.09 through 1.6.27 is vulnerable to path traversal. Unauthenticated remote attacker is able to exploit a vulnerable endpoint and construct payloads that allow to read content of any file accessible by the the web server process.This issue was fixed in version 1.6.28.

## References
- https://cert.pl/en/posts/2026/03/CVE-2026-3013
- https://github.com/coppermine-gallery/cpg1.6.x/releases/tag/v1.6.28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/3xxx/CVE-2026-3013.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-3013
- https://github.com/coppermine-gallery/cpg1.6.x
