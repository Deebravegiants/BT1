# [H] OpenEMR: Therapy Group Sensitivity ACL No Longer Enforced

## Summary
Severity: High
Advisory: CVE-2026-32123
Aliases: GHSA-j4mm-wg7q-v57q
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-32123
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to 8.0.0.1, sensitivity checks for group encounters are broken because the code only consults form_encounter for sensitivity, while group encounters store sensitivity in form_groups_encounter. As a result, sensitivity is never correctly applied to group encounters, and users who should be restricted from viewing sensitive (e.g. mental health) encounters can view them. This vulnerability is fixed in 8.0.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32123.json
- https://github.com/openemr/openemr/security/advisories/GHSA-j4mm-wg7q-v57q
- https://nvd.nist.gov/vuln/detail/CVE-2026-32123
