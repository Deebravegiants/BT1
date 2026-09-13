# [M] CVE-2024-56169

## Summary
Severity: Medium
Advisory: CVE-2024-56169
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-12-18
Source: https://osv.dev/vulnerability/CVE-2024-56169
Type: osv

## Details
A validation integrity issue was discovered in Fort through 1.6.4 before 2.0.0. RPKI Relying Parties (such as Fort) are supposed to maintain a backup cache of the remote RPKI data. This can be employed as a fallback in case a new fetch fails or yields incorrect files. However, the product currently uses its cache merely as a bandwidth saving tool (because fetching is performed through deltas). If a fetch fails midway or yields incorrect files, there is no viable fallback. This leads to incomplete route origin validation data.

## References
- https://nicmx.github.io/FORT-validator/CVE.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56169.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56169
- https://github.com/NICMx/FORT-validator/issues/82
