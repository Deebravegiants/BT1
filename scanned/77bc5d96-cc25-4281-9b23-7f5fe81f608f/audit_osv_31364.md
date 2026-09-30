# [M] SSRF in gaizhenbiao/chuanhuchatgpt

## Summary
Severity: Medium
Advisory: CVE-2025-0188
Aliases: PYSEC-2025-98
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2025-0188
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability was discovered in gaizhenbiao/chuanhuchatgpt version 20240914. The vulnerability allows an attacker to construct a response link by saving the response in a folder named after the SHA-1 hash of the target URL. This enables the attacker to access the response directly, potentially leading to unauthorized access to internal systems, data theft, service disruption, or further attacks such as port scanning and accessing metadata endpoints.

## References
- https://huntr.com/bounties/879d2470-eca5-49c0-b3d1-57469cfff412
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0188.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0188
