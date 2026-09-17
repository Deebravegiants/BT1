# [M] Sensitive Data Exposure in elFinder

## Summary
Severity: Medium
Advisory: GHSA-jcgc-vxqg-85xx
CVE: CVE-2019-5884
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jcgc-vxqg-85xx
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.45

## Details
`php/elFinder.class.php` in elFinder before 2.1.45 leaks information if PHP's curl extension is enabled and `safe_mode` or `open_basedir` is not set.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5884
- https://github.com/Studio-42/elFinder/commit/f133163f2d754584de65d718b2fde96191557316
- https://github.com/Studio-42/elFinder/releases/tag/2.1.45
