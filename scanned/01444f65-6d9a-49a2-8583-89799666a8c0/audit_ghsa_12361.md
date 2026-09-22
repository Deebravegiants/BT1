# [H] ThinkAdmin arbitrary file upload vulnerability

## Summary
Severity: High
Advisory: GHSA-7gq9-p94f-g5v9
CVE: CVE-2023-48966
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-04
Source: https://github.com/advisories/GHSA-7gq9-p94f-g5v9
Type: github-advisory

## Affected
- Packagist: `zoujingli/thinkadmin` — affected >=0

## Details
An arbitrary file upload vulnerability in the component /admin/api.upload/file of ThinkAdmin v6.1.53 allows attackers to execute arbitrary code via a crafted Zip file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48966
- https://github.com/1dreamGN/CVE/blob/main/ThinkAdmin%20directory%20traversal%2Bfile%20upload%20getshell.md
- https://github.com/zoujingli/ThinkAdmin
