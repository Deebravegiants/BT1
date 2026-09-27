# [H] elFinder Server Side Request Forgery (SSRF)

## Summary
Severity: High
Advisory: GHSA-3qhm-qfj3-4rrx
CVE: CVE-2019-6257
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3qhm-qfj3-4rrx
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.49

## Details
A Server Side Request Forgery (SSRF) vulnerability in elFinder before 2.1.49 could allow a malicious user to access the content of internal network resources. This occurs in `get_remote_contents()` in `php/elFinder.class.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6257
- https://github.com/Studio-42/elFinder/commit/2f522db8f037a66ce9040ee0b216aa4a0359286c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/studio-42/elfinder/CVE-2019-6257.yaml
- https://github.com/Studio-42/elFinder
- https://github.com/Studio-42/elFinder/blob/2.1.49/Changelog
- https://github.com/Studio-42/elFinder/releases/tag/2.1.49
