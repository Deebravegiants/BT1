# [H] Authentication Bypass in langgenius/dify

## Summary
Severity: High
Advisory: CVE-2024-12776
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12776
Type: osv

## Details
In langgenius/dify v0.10.1, the `/forgot-password/resets` endpoint does not verify the password reset code, allowing an attacker to reset the password of any user, including administrators. This vulnerability can lead to a complete compromise of the application.

## References
- https://huntr.com/bounties/00a8b403-7da5-431e-afa3-40339cf734bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12776.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12776
