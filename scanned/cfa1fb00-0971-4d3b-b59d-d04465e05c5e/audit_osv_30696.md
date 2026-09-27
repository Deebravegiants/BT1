# [M] CVE-2024-55089

## Summary
Severity: Medium
Advisory: CVE-2024-55089
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:L/A:N)
Published: 2024-12-18
Source: https://osv.dev/vulnerability/CVE-2024-55089
Type: osv

## Details
Rhymix before 2.1.24 is vulnerable to Server-Side Request Forgery (SSRF) in the background import data function because XML documents may contain external entities.

## References
- https://rhymix.org/news/1909005
- https://tasteful-stamp-da4.notion.site/CVE-2024-55089-15b1e0f227cb8064a563c697709b7530?pvs=73
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55089.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-55089
- https://github.com/rhymix/rhymix/commit/464985b1ef382cc8cf852e9b028a960aa58b40c3
