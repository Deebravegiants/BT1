# [H] Plane Vulnerable to Full Read SSRF via Favicon Fetching in "Add Link" Feature

## Summary
Severity: High
Advisory: CVE-2026-27706
Aliases: GHSA-jcc6-f9v6-f7jw
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27706
Type: osv

## Details
Plane is an an open-source project management tool. Prior to version 1.2.2, a Full Read Server-Side Request Forgery (SSRF) vulnerability has been identified in the "Add Link" feature. This flaw allows an authenticated attacker with general user privileges to send arbitrary GET requests to the internal network and exfiltrate the full response body. By exploiting this vulnerability, an attacker can steal sensitive data from internal services and cloud metadata endpoints. Version 1.2.2 fixes the issue.

## References
- https://github.com/makeplane/plane/releases/tag/v1.2.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27706.json
- https://github.com/makeplane/plane/security/advisories/GHSA-jcc6-f9v6-f7jw
- https://nvd.nist.gov/vuln/detail/CVE-2026-27706
