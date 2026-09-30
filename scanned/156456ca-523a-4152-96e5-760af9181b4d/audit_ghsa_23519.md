# [M] phpThumb is vulnerable to Server-Side Request Forgery (SSRF)

## Summary
Severity: Medium
Advisory: GHSA-3747-gjc9-vvg6
CVE: CVE-2013-6919
CWE: CWE-918
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3747-gjc9-vvg6
Type: github-advisory

## Affected
- Packagist: `james-heinrich/phpthumb` — affected >=0 <1.7.12

## Details
The default configuration of phpThumb before 1.7.12 has a false value for the disable_debug option, which allows remote attackers to conduct Server-Side Request Forgery (SSRF) attacks via the src parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6919
- https://github.com/JamesHeinrich/phpThumb/commit/457a37d4a22ac9cdbbfe19577376622e58df81b0
- https://github.com/JamesHeinrich/phpThumb
- https://github.com/JamesHeinrich/phpThumb/blob/7ee966b38ddd7eb4d8091389aa514604710711c8/docs/phpthumb.changelog.txt#L106
- http://www.rafayhackingarticles.net/2013/11/phpthumb-server-side-request-forgery.html
