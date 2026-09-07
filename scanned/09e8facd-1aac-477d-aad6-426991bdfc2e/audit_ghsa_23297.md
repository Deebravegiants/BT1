# [H] GeniXCMS arbitrary PHP code execution

## Summary
Severity: High
Advisory: GHSA-2f6r-892p-69g5
CVE: CVE-2017-14763
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2f6r-892p-69g5
Type: github-advisory

## Affected
- Packagist: `genix/cms` — affected 1.1.4

## Details
In the Install Themes page in GeniXCMS 1.1.4, remote authenticated users can execute arbitrary PHP code via a .php file in a ZIP archive of a theme.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14763
- https://github.com/GeniXCMS/GeniXCMS
- http://ph0rse.me/2017/09/21/GeniXCMS-1-1-4%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC-getshell
