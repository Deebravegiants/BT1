# [M] October CMS XSS In Caption Tag of Profile

## Summary
Severity: Medium
Advisory: GHSA-9hq8-v2jc-qj4r
CVE: CVE-2015-5612
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9hq8-v2jc-qj4r
Type: github-advisory

## Affected
- Packagist: `october/october` — affected >=0 <1.0.319

## Details
Cross-site scripting (XSS) vulnerability in October CMS build 271 and earlier allows remote attackers to inject arbitrary web script or HTML via the caption tag of a profile image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5612
- https://github.com/octobercms/october/issues/1302
- https://github.com/octobercms/october/commit/8a4ac533e5cd6b8f92e9ef19fbfbb2f505dc7a9a
- http://www.openwall.com/lists/oss-security/2015/07/21/5
- http://www.openwall.com/lists/oss-security/2015/07/22/3
