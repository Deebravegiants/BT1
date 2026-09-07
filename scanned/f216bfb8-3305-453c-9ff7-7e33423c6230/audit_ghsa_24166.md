# [C] elFinder Path Traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-45x3-mw7q-wf7f
CVE: CVE-2018-9109
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-45x3-mw7q-wf7f
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.36

## Details
Studio 42 elFinder before 2.1.36 has a directory traversal vulnerability in `elFinder.class.php` with the `zipdl()` function that can allow a remote attacker to download files accessible by the web server process and delete files owned by the account running the web server process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-9109
- https://github.com/Studio-42/elFinder/commit/157f471d7e48f190f74e66eb5bc73360b5352fd3
- https://github.com/Studio-42/elFinder
- https://github.com/Studio-42/elFinder/releases/tag/2.1.36
- https://github.com/Studio-42/elFinder/wiki/Advisory-about-vulnerability-of-CVE-2018-9109-and-CVE-2018-9110
