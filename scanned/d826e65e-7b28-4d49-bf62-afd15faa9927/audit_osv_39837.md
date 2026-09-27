# [M] Spring Cloud Config Server Monitor Endpoint Does Not Validate Webhook Requests

## Summary
Severity: Medium
Advisory: CVE-2026-47837
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-47837
Type: osv

## Details
Missing Authentication for Critical Function vulnerability in Spring Spring Cloud Config allows Webhook requests to Spring Cloud Config Server's /monitor endpoint are not validated.

This issue affects Spring Cloud Config: from 5.0.0 through 5.0.4, from 4.3.0 through 4.3.4, from 4.0.0 through 4.2.8, and through 3.1.14.

## References
- https://spring.io/security/cve-2026-47837
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47837.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47837
