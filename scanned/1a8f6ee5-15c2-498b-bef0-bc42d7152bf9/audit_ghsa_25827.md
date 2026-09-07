# [C] Path Traversal in Studio-42 elFinder through 2.1.60

## Summary
Severity: Critical
Advisory: GHSA-7q88-jxvp-9gp2
CVE: CVE-2022-26960
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-03-22
Source: https://github.com/advisories/GHSA-7q88-jxvp-9gp2
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.61

## Details
`connector.minimal.php` in std42 elFinder through 2.1.60 is affected by path traversal. This allows unauthenticated remote attackers to read, write, and browse files outside the configured document root. This is due to improper handling of absolute file paths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26960
- https://github.com/Studio-42/elFinder/commit/3b758495538a448ac8830ee3559e7fb2c260c6db
- https://www.synacktiv.com/publications/elfinder-the-story-of-a-repwning.html
