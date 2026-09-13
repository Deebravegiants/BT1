# [M] Mautic vulnerable to secret data extraction via elfinder

## Summary
Severity: Medium
Advisory: GHSA-438m-6mhw-hq5w
CVE: CVE-2025-9822
CWE: CWE-283
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-438m-6mhw-hq5w
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=4.4.0 <4.4.17
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.2.8
- Packagist: `mautic/core` — affected >=6.0.0-alpha <6.0.5

## Details
### Summary
_A user with administrator rights can change the configuration of the mautic application and extract secrets that are not normally available._


### Impact
_An administrator who usually does not have access to certain parameters, such as database credentials, can disclose them._

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-438m-6mhw-hq5w
- https://nvd.nist.gov/vuln/detail/CVE-2025-9822
- https://github.com/mautic/mautic/commit/882c2c5be646e36f7b91e7c4b24f71aafa617cd5
- https://github.com/mautic/mautic/commit/a310b1933de7cfefec03382a4d8c0d9dbbaa0600
- https://github.com/mautic/mautic
