# [C] Directory Traversal in Studio 42 elFinder

## Summary
Severity: Critical
Advisory: GHSA-44p8-c3wv-f28r
CVE: CVE-2018-9110
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-44p8-c3wv-f28r
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=2.1.12 <2.1.37

## Details
Studio 42 elFinder before 2.1.37 has a directory traversal vulnerability in `elFinder.class.php` with the `zipdl()` function that can allow a remote attacker to download files accessible by the web server process and delete files owned by the account running the web server process. NOTE: this issue exists because of an incomplete fix for CVE-2018-9109.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-9110
- https://github.com/Studio-42/elFinder/commit/e6351557b86cc10a7651253d2d2aff7f6b918f8e
- https://github.com/Studio-42/elFinder/releases/tag/2.1.37
- https://github.com/Studio-42/elFinder/wiki/Advisory-about-vulnerability-of-CVE-2018-9109-and-CVE-2018-9110
