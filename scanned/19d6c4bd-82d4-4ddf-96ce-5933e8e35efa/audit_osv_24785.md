# [C] CVE-2023-26770

## Summary
Severity: Critical
Advisory: CVE-2023-26770
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-04
Source: https://osv.dev/vulnerability/CVE-2023-26770
Type: osv

## Details
TaskCafe 0.3.2 lacks validation in the Cookie value. Any unauthenticated attacker who knows a registered UserID can change the password of that user.

## References
- https://bishopfox.com/blog/taskcafe-version-0-3-2-advisory
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26770.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26770
- https://github.com/JordanKnott/taskcafe
