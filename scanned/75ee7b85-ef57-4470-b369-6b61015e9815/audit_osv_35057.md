# [M] FreshRSS globally denies access to feed via proxy modifying to 429 Retry-After

## Summary
Severity: Medium
Advisory: CVE-2025-68148
Aliases: GHSA-qw34-frg7-gf78
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-12-26
Source: https://osv.dev/vulnerability/CVE-2025-68148
Type: osv

## Details
FreshRSS is a free, self-hostable RSS aggregator. From version 1.27.0 to before 1.28.0, An attacker could globally deny access to feeds via proxy modifying to 429 Retry-After for a large list of feeds on given instance, making it unusable for majority of users. This issue has been patched in version 1.28.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68148.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-qw34-frg7-gf78
- https://nvd.nist.gov/vuln/detail/CVE-2025-68148
- https://github.com/FreshRSS/FreshRSS/commit/7d4854a0a4f5665db599f18c34035786465639f3
- https://github.com/FreshRSS/FreshRSS/pull/8029
