# [H] Bolt Unrestricted Upload of File with Dangerous Type

## Summary
Severity: High
Advisory: GHSA-gmg5-f2gm-p3h7
CVE: CVE-2019-9185
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gmg5-f2gm-p3h7
Type: github-advisory

## Affected
- Packagist: `bolt/bolt` — affected >=0 <3.6.5

## Details
`Controller/Async/FilesystemManager.php` in the filemanager in Bolt before 3.6.5 allows remote attackers to execute arbitrary PHP code by renaming a previously uploaded file to have a `.php` extension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9185
- https://github.com/bolt/bolt/pull/7745
- https://github.com/bolt/bolt
- https://github.com/bolt/bolt/blob/v3.6.5/changelog.md
- https://github.com/bolt/bolt/releases/tag/v3.6.5
- https://www.hacksecproject.com/?p=293
