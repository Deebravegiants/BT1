# [C] OpenProject is Vulnerable to Code Execution in E-Mail function

## Summary
Severity: Critical
Advisory: CVE-2026-22601
Aliases: GHSA-9vrv-7h26-c7jc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2026-22601
Type: osv

## Details
OpenProject is an open-source, web-based project management software. For OpenProject version 16.6.1 and below, a registered administrator can execute arbitrary command by configuring sendmail binary path and sending a test email. This issue has been patched in version 16.6.2.

## References
- https://github.com/opf/openproject/releases/tag/v16.6.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22601.json
- https://github.com/opf/openproject/security/advisories/GHSA-9vrv-7h26-c7jc
- https://nvd.nist.gov/vuln/detail/CVE-2026-22601
