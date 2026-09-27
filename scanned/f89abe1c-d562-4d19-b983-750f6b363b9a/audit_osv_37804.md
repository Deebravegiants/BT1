# [M] OpenEMR has Out-of-Band Server-Side Request Forgery (OOB SSRF)

## Summary
Severity: Medium
Advisory: CVE-2026-33321
Aliases: GHSA-5pc3-2crw-96rv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:L/SC:L/SI:L/SA:L)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-33321
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to 8.0.0.2, users with the `Notes - my encounters` role can fill Eye Exam forms in patient encounters. The answers to the form can be printed out in PDF form. An Out-of-Band Server-Side Request Forgery (OOB SSRF) vulnerability was identified in the PDF creation function where the form answers are parsed as unescaped HTML, allowing an attacker to forge requests from the server made to external or internal resources. Version 8.0.0.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33321.json
- https://github.com/openemr/openemr/security/advisories/GHSA-5pc3-2crw-96rv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33321
- https://github.com/openemr/openemr/commit/dccc962f06bdf6105ca85c277915167caf3e7c28
