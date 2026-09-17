# [H] OpenEMR has SQL Injection in CAMOS Form

## Summary
Severity: High
Advisory: CVE-2026-33917
Aliases: GHSA-r6xq-mfwf-wgq8
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-33917
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Versions prior to 8.0.0.3 contais a SQL injection vulnerability in the ajax_save CAMOS form that can be exploited by authenticated attackers. The vulnerability exists due to insufficient input validation in the ajax_save page in the CAMOS form. Version 8.0.0.3 patches the issue.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33917.json
- https://github.com/openemr/openemr/security/advisories/GHSA-r6xq-mfwf-wgq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-33917
- https://github.com/openemr/openemr/commit/4d48821d18e4125508d8217c43b09233c7f7e17f
