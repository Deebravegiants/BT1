# [M] Weblate vulnerabler to improper sanitization of project backups

## Summary
Severity: Medium
Advisory: CVE-2024-39303
Aliases: GHSA-jfgp-674x-6q4p, PYSEC-2026-2041
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:L/I:L/A:N)
Published: 2024-07-01
Source: https://osv.dev/vulnerability/CVE-2024-39303
Type: osv

## Details
Weblate is a web based localization tool. Prior to version 5.6.2, Weblate didn't correctly validate filenames when restoring project backup. It may be possible to gain unauthorized access to files on the server using a crafted ZIP file. This issue has been addressed in Weblate 5.6.2. As a workaround, do not allow untrusted users to create projects.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39303.json
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-jfgp-674x-6q4p
- https://nvd.nist.gov/vuln/detail/CVE-2024-39303
- https://github.com/WeblateOrg/weblate/commit/b6a7eace155fa0feaf01b4ac36165a9c5e63bfdd
