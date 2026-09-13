# [M] Server-Side Request Forgery (SSRF) in langgenius/dify

## Summary
Severity: Medium
Advisory: CVE-2024-11822
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-11822
Type: osv

## Details
langgenius/dify version 0.9.1 contains a Server-Side Request Forgery (SSRF) vulnerability. The vulnerability exists due to improper handling of the api_endpoint parameter, allowing an attacker to make direct requests to internal network services. This can lead to unauthorized access to internal servers and potentially expose sensitive information, including access to the AWS metadata endpoint.

## References
- https://huntr.com/bounties/f3042029-5d4e-41c6-850d-bbe02fae6592
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11822.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11822
