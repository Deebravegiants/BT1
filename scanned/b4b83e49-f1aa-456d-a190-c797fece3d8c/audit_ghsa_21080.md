# [M] Known v1.3.1 Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-g688-7j3c-h9f3
CVE: CVE-2022-31290
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-09
Source: https://github.com/advisories/GHSA-g688-7j3c-h9f3
Type: github-advisory

## Affected
- Packagist: `idno/known` — affected >=0

## Details
A cross-site scripting (XSS) vulnerability in Known v1.3.1 allows authenticated attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the Your Name text field.

The researcher report indicates that versions 1.3.1 and prior are vulnerable. Version 1.2.2 is the last version tagged on GitHub and in Packagist, and development related to the 1.3.x branch is currently on the `dev` branch of the idno/known repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31290
- https://blog.jitendrapatro.me/multiple-vulnerabilities-in-idno-known-php-cms-software
- https://github.com/idno/known
- https://withknown.com
- http://docs.withknown.com/en/latest/install/index.html
