# [M] Fork CMS XSS via Highlight Parameter

## Summary
Severity: Medium
Advisory: GHSA-v3fg-x8jw-m974
CVE: CVE-2012-1209
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-v3fg-x8jw-m974
Type: github-advisory

## Affected
- Packagist: `forkcms/forkcms` — affected >=0 <3.2.5

## Details
Cross-site scripting (XSS) vulnerability in `backend/core/engine/base.php` in Fork CMS 3.2.4 and possibly other versions before 3.2.5 allows remote attackers to inject arbitrary web script or HTML via the highlight parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1209
- https://github.com/forkcms/forkcms/commit/c8ec9c58a6b3c46cdd924532c1de99bcda6072ed
- https://github.com/forkcms/forkcms/commit/df75e0797a6540c4d656969a2e7df7689603b2cf
- https://exchange.xforce.ibmcloud.com/vulnerabilities/73393
- https://github.com/forkcms/forkcms
- http://www.fork-cms.com/blog/detail/fork-cms-3-2-5-released
