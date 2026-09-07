# [M] CakePHP: View::element() is missing a path containment check

## Summary
Severity: Medium
Advisory: GHSA-wpvj-hjcr-h3p2
CVE: CVE-2026-48820
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-wpvj-hjcr-h3p2
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=5.3.0 <5.3.6
- Packagist: `cakephp/cakephp` — affected >=5.2.0 <5.2.13
- Packagist: `cakephp/cakephp` — affected >=5.0.0 <5.1.7
- Packagist: `cakephp/cakephp` — affected >=4.6.0 <4.6.4
- Packagist: `cakephp/cakephp` — affected >=0 <4.5.11

## Details
### Impact
`View::_getElementFileName()` does not check that the resolved element path is within the application/plugin view template paths. When element names are created with specifically crafted user-supplied data this weakness can be leveraged to include other PHP files on the server.

### Patches
Patched releases are available in 5.3.6, 5.2.13, 5.1.7, 4.6.4, and 4.5.11.

### Workarounds
If developers are not using user-supplied data in element names, no action is required.

## References
- https://github.com/cakephp/cakephp/security/advisories/GHSA-wpvj-hjcr-h3p2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48820
- https://github.com/cakephp/cakephp
