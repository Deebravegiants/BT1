# [H] Improper file handling in concrete5/core

## Summary
Severity: High
Advisory: GHSA-g3p2-hfqr-9m25
CVE: CVE-2021-22968
CWE: CWE-330, CWE-98
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-23
Source: https://github.com/advisories/GHSA-g3p2-hfqr-9m25
Type: github-advisory

## Affected
- Packagist: `concrete5/core` — affected >=0 <8.5.7

## Details
A bypass of adding remote files in Concrete CMS (previously concrete5) File Manager leads to remote code execution in Concrete CMS (concrete5) versions 8.5.6 and below. The external file upload feature stages files in the public directory even if they have disallowed file extensions. They are stored in a directory with a random name, but it's possible to stall the uploads and brute force the directory name. You have to be an admin with the ability to upload files, but this bug gives you the ability to upload restricted file types and execute them depending on server configuration. To fix this, a check for allowed file extensions was added before downloading files to a tmp directory

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22968
- https://hackerone.com/reports/1350444
- https://documentation.concretecms.org/developers/introduction/version-history/857-release-notes
- https://github.com/olsgreen/concrete5-core
