# [M] SSRF in langgenius/dify

## Summary
Severity: Medium
Advisory: CVE-2024-12775
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12775
Type: osv

## Details
langgenius/dify version 0.10.1 contains a Server-Side Request Forgery (SSRF) vulnerability in the test functionality for the Create Custom Tool option via the REST API `POST /console/api/workspaces/current/tool-provider/api/test/pre`. Attackers can set the `url` in the `servers` dictionary in OpenAI's schema with arbitrary URL targets, allowing them to abuse the victim server's credentials to access unauthorized web resources.

## References
- https://huntr.com/bounties/e90e929a-9bc9-46ad-a5e5-1f6f124d0f12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12775.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12775
