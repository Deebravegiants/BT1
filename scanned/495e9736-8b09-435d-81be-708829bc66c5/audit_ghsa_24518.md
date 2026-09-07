# [M] Magmi XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r8vh-cm9f-rc29
CVE: CVE-2017-7391
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-r8vh-cm9f-rc29
Type: github-advisory

## Affected
- Packagist: `dweeves/magmi` — affected >=0 <0.7.24

## Details
A Cross-Site Scripting (XSS) was discovered in Magmi 0.7.22. The vulnerability exists due to insufficient filtration of user-supplied data (prefix) passed to the `magmi-git-master/magmi/web/ajax_gettime.php` URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7391
- https://github.com/dweeves/magmi-git/issues/522
- https://github.com/dweeves/magmi-git/pull/525
- https://github.com/dweeves/magmi-git/commit/a9566b141b58bf40a9dd904a74e6efcc225a28a3
- https://web.archive.org/web/20210125191718/http://www.securityfocus.com/bid/97311
