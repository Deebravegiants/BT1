# [H] OpenEMR allows links sent via Secure Messaging to be opened in OpenEMR and Portal

## Summary
Severity: High
Advisory: CVE-2025-68277
Aliases: GHSA-566c-8c52-2jch
CVSS: 7.5 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:A/VC:H/VI:H/VA:L/SC:H/SI:H/SA:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2025-68277
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 7.0.4, when a link is sent via Secure Messaging, clicking the link opens the website within the OpenEMR/Portal site. This behavior could be exploited for phishing. Version 7.0.4 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68277.json
- https://github.com/openemr/openemr/security/advisories/GHSA-566c-8c52-2jch
- https://nvd.nist.gov/vuln/detail/CVE-2025-68277
- https://github.com/openemr/openemr/commit/11ec62d1683571a629734fba66f7fb68d0bdc312
