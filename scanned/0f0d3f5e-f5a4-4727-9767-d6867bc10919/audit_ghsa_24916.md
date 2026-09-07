# [M] Fork CMS Multiple XSS Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-j5fj-m342-mgcm
CVE: CVE-2012-1188
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j5fj-m342-mgcm
Type: github-advisory

## Affected
- Packagist: `forkcms/forkcms` — affected >=0 <3.2.7

## Details
Multiple cross-site scripting (XSS) vulnerabilities in Fork CMS before 3.2.7 allow remote attackers to inject arbitrary web script or HTML via the (1) type or (2) querystring parameters to `private/en/error` or (3) name parameter to `private/en/locale/index`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-1188
- https://github.com/forkcms/forkcms/commit/1269fe8b3813c7b7d5552a2b88bc2e7bd4d0c1f9
- https://github.com/forkcms/forkcms/commit/995220182068518e89019a265d113518f6566407
- https://exchange.xforce.ibmcloud.com/vulnerabilities/73605
- https://github.com/forkcms/forkcms
- https://web.archive.org/web/20120401204345/http://www.securityfocus.com/bid/52236
- https://web.archive.org/web/20200229131647/https://www.immuniweb.com/advisory/HTB23075
- http://www.fork-cms.com/blog/detail/fork-cms-3-2-7-released
