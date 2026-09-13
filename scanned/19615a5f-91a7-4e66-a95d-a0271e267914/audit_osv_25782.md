# [M] Autolab has Path Traversal vulnerability in Assessment functionality

## Summary
Severity: Medium
Advisory: CVE-2023-44395
Aliases: GHSA-h8wq-ghfq-5hfx
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-22
Source: https://osv.dev/vulnerability/CVE-2023-44395
Type: osv

## Details
Autolab is a course management service that enables instructors to offer autograded programming assignments to their students over the Web. Path traversal vulnerabilities were discovered in Autolab's assessment functionality in versions of Autolab prior to 2.12.0, whereby instructors can perform arbitrary file reads. Version 2.12.0 contains a patch. There are no feasible workarounds for this issue.

## References
- https://github.com/autolab/Autolab/releases/tag/v2.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/44xxx/CVE-2023-44395.json
- https://github.com/autolab/Autolab/security/advisories/GHSA-h8wq-ghfq-5hfx
- https://nvd.nist.gov/vuln/detail/CVE-2023-44395
- https://www.stackhawk.com/blog/rails-path-traversal-guide-examples-and-prevention/
