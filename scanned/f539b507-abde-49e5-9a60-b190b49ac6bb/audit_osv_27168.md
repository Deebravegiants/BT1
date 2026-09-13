# [H] Improper Restriction of Excessive Authentication Attempts in langgenius/dify

## Summary
Severity: High
Advisory: CVE-2024-12039
CVSS: 7.4 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12039
Type: osv

## Details
langgenius/dify version v0.10.1 contains a vulnerability where there are no limits applied to the number of code guess attempts for password reset. This allows an unauthenticated attacker to reset owner, admin, or other user passwords within a few hours by guessing the six-digit code, resulting in a complete compromise of the application.

## References
- https://huntr.com/bounties/61af30d5-6055-4c6c-8a55-3fa43dada512
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12039.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12039
