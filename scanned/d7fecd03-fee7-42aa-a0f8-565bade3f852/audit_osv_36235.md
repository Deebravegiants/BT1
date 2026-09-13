# [H] GLPI affected by Remote Code Execution via malicious upload

## Summary
Severity: High
Advisory: CVE-2026-22248
Aliases: GHSA-c9q3-mcxq-9vr4
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-22248
Type: osv

## Details
GLPI is an open-source asset and IT management software package that provides ITIL Service Desk features, licenses tracking and software auditing. From 11.0.0 to before 11.0.5, an authenticated technician user can upload a malicious file and trigger its execution through an unsafe PHP instantiation. This vulnerability is fixed in 11.0.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22248.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-c9q3-mcxq-9vr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-22248
