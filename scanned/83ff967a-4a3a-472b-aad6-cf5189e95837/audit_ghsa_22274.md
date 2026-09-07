# [M] imdbphp Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-8jxq-gpmr-h4g4
CVE: CVE-2017-7204
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-8jxq-gpmr-h4g4
Type: github-advisory

## Affected
- Packagist: `imdbphp/imdbphp` — affected >=0 <5.2.0

## Details
A Cross-Site Scripting (XSS) was discovered in imdbphp 5.1.1. The vulnerability exists due to insufficient filtration of user-supplied data (name) passed to the "imdbphp-master/demo/search.php" URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7204
- https://github.com/tboothman/imdbphp/issues/88
- https://github.com/tboothman/imdbphp/commit/5875c75c6ca6a53dc4faaaeca973150d380e88e2
- https://github.com/tboothman/imdbphp
- http://www.securityfocus.com/bid/97002
