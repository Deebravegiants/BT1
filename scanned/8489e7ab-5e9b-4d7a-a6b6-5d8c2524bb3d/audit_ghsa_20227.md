# [M] Neos CMS vulnerable to XSS in various backend modules

## Summary
Severity: Medium
Advisory: GHSA-7m9h-v68w-pfw3
CVE: CVE-2022-30429
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-7m9h-v68w-pfw3
Type: github-advisory

## Affected
- Packagist: `neos/neos` — affected >=3.3.0 <4.4.0
- Packagist: `neos/neos` — affected >=5.3.0 <5.3.10
- Packagist: `neos/neos` — affected >=7.0.0 <7.0.9
- Packagist: `neos/neos` — affected >=7.1.0 <7.1.7
- Packagist: `neos/neos` — affected >=7.2.0 <7.2.6
- Packagist: `neos/neos` — affected >=7.3.0 <7.3.4
- Packagist: `neos/neos` — affected >=8.0.0 <8.0.2

## Details
Multiple cross-site scripting (XSS) vulnerabilities in Neos CMS allow attackers with the editor role or higher to inject arbitrary script or HTML code using the editor function, the deletion of assets, or a workspace title. The vulnerabilities were found in versions 3.3.29 and 8.0.1 and could also be present in all intermediate versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30429
- https://github.com/FriendsOfPHP/security-advisories/blob/master/neos/neos/CVE-2022-30429.yaml
- https://github.com/neos/neos
- https://it-sec.de/unbekannte-schwachstellen-in-neos-cms
- https://www.neos.io/blog/xss-in-various-backend-modules.html
