# [C] PEAR::Archive_Tar Directory Traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-f3xw-vgc7-f7h8
CVE: CVE-2006-0931
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-f3xw-vgc7-f7h8
Type: github-advisory

## Affected
- Packagist: `pear/archive_tar` — affected >=1.2 <1.3.2

## Details
Directory traversal vulnerability in PEAR::Archive_Tar 1.2, and other versions before 1.3.2, allows remote attackers to create and overwrite arbitrary files via certain crafted pathnames in a TAR archive.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-0931
- https://github.com/pear/Archive_Tar
- http://pear.php.net/bugs/bug.php?id=6933
- http://pear.php.net/package/Archive_Tar/download
- http://www.hamid.ir/security/phptar.txt
