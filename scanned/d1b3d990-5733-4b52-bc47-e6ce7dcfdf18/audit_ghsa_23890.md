# [M] MantisBT unauthorized users able to access private files

## Summary
Severity: Medium
Advisory: GHSA-xjmx-cprh-646r
CVE: CVE-2020-25781
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xjmx-cprh-646r
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.24.3

## Details
An issue was discovered in file_download.php in MantisBT before 2.24.3. Users without access to view private issue notes are able to download the (supposedly private) attachments linked to these notes by accessing the corresponding file download URL directly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25781
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=27039
- http://github.com/mantisbt/mantisbt/commit/5595c90f11c48164331a20bb9c66098980516e93
- http://github.com/mantisbt/mantisbt/commit/9de20c09e5a557e57159a61657ce62f1a4f578fe
