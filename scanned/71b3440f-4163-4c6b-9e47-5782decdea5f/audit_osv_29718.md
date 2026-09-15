# [M] CVE-2024-45751

## Summary
Severity: Medium
Advisory: CVE-2024-45751
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-09-06
Source: https://osv.dev/vulnerability/CVE-2024-45751
Type: osv

## Details
tgt (aka Linux target framework) before 1.0.93 attempts to achieve entropy by calling rand without srand. The PRNG seed is always 1, and thus the sequence of challenges is always identical.

## References
- http://www.openwall.com/lists/oss-security/2024/09/07/2
- https://github.com/fujita/tgt/compare/v1.0.92...v1.0.93
- https://lists.debian.org/debian-lts-announce/2024/11/msg00033.html
- https://www.openwall.com/lists/oss-security/2024/09/07/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45751.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45751
- https://github.com/fujita/tgt/pull/67
