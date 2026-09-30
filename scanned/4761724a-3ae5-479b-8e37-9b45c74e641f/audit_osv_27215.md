# [H] SSRF in comfyanonymous/comfyui

## Summary
Severity: High
Advisory: CVE-2024-12882
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12882
Type: osv

## Details
comfyanonymous/comfyui version v0.2.4 suffers from a non-blind Server-Side Request Forgery (SSRF) vulnerability. This vulnerability can be exploited by combining the REST APIs `POST /internal/models/download` and `GET /view`, allowing attackers to abuse the victim server's credentials to access unauthorized web resources.

## References
- https://huntr.com/bounties/e8768cb1-6a80-40c1-9cdf-bcd21f01f85a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12882.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12882
