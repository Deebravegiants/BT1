# [M] CVE-2024-1063

## Summary
Severity: Medium
Advisory: CVE-2024-1063
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-01-30
Source: https://osv.dev/vulnerability/CVE-2024-1063
Type: osv

## Details
Appwrite <= v1.4.13 is affected by a Server-Side Request Forgery (SSRF) via the '/v1/avatars/favicon' endpoint due to an incomplete fix of CVE-2023-27159.

## References
- https://www.tenable.com/security/research/tra-2024-03
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1063.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1063
- https://github.com/appwrite/appwrite
