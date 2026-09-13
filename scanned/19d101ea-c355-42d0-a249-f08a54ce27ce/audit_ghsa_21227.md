# [M] Known vulnerable to code execution via SVG file in v1.3.1

## Summary
Severity: Medium
Advisory: GHSA-5jgj-h9wp-53fr
CVE: CVE-2022-32115
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-09
Source: https://github.com/advisories/GHSA-5jgj-h9wp-53fr
Type: github-advisory

## Affected
- Packagist: `idno/known` — affected >=0

## Details
An issue in the isSVG() function of Known v1.3.1 allows attackers to execute arbitrary code via a crafted SVG file.

The researcher report indicates that versions 1.3.1 and prior are vulnerable. Version 1.2.2 is the last version tagged on GitHub and in Packagist, and development related to the 1.3.x branch is currently on the `dev` branch of the idno/known repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32115
- https://github.com/idno/known/commit/80b716a8392fb71cfce84d03aaf7c045c62f6350
- https://blog.jitendrapatro.me/multiple-vulnerabilities-in-idno-known-php-cms-software
- https://github.com/idno/known
- https://github.com/idno/known/blob/dev/composer.json#L4
- https://withknown.com
