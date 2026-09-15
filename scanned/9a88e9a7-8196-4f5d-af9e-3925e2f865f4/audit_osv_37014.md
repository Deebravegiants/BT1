# [M] MarkUs: YAML alias (‘billion laughs’) DoS in config upload

## Summary
Severity: Medium
Advisory: CVE-2026-27807
Aliases: GHSA-m9rx-85mx-q9h6
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-27807
Type: osv

## Details
MarkUs is a web application for the submission and grading of student assignments. Prior to version 2.9.4, MarkUs allows course instructors to upload YAML files to create/update various entities (e.g., assignment settings). These YAML files are parsed with aliases enabled. This issue has been patched in version 2.9.4.

## References
- https://github.com/MarkUsProject/Markus/releases/tag/v2.9.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27807.json
- https://github.com/MarkUsProject/Markus/security/advisories/GHSA-m9rx-85mx-q9h6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27807
