# [C] Weblate is vulnerable to RCE through Git config file overwrite

## Summary
Severity: Critical
Advisory: GHSA-8vcg-cfxj-p5m3
CVE: CVE-2025-68398
CWE: CWE-20, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-18
Source: https://github.com/advisories/GHSA-8vcg-cfxj-p5m3
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <5.15.1

## Details
### Impact

It was possible to overwrite Git configuration remotely and override some of its behavior.


### Resources

Thanks to Jason Marcello for responsible disclosure.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-8vcg-cfxj-p5m3
- https://nvd.nist.gov/vuln/detail/CVE-2025-68398
- https://github.com/WeblateOrg/weblate/pull/17330
- https://github.com/WeblateOrg/weblate/pull/17345
- https://github.com/WeblateOrg/weblate/commit/4837a4154390f7c1d03c0e398aa6439dcfa361b4
- https://github.com/WeblateOrg/weblate/commit/dd8c9d7b00eebe28770fa0e2cd96126791765ea7
- https://github.com/WeblateOrg/weblate
- https://github.com/WeblateOrg/weblate/releases/tag/weblate-5.15.1
