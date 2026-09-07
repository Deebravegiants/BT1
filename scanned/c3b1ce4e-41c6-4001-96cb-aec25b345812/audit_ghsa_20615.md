# [M] Cross site scripting in getkirby/starterkit

## Summary
Severity: Medium
Advisory: GHSA-4m2g-668v-jwjx
CVE: CVE-2022-35174
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-08-19
Source: https://github.com/advisories/GHSA-4m2g-668v-jwjx
Type: github-advisory

## Affected
- Packagist: `getkirby/starterkit` — affected >=0

## Details
A stored cross-site scripting (XSS) vulnerability in Kirby's Starterkit v3.7.0.2 allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the Tags field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-35174
- https://github.com/getkirby/starterkit
- https://owasp.org/www-community/attacks/xss
- https://www.youtube.com/watch?v=0lngc_zPTSg
