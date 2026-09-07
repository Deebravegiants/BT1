# [H] Improper Neutralization of Text-Values in Object Version Preview

## Summary
Severity: High
Advisory: GHSA-w6j8-jc36-x5q9
CVE: CVE-2021-39166
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-w6j8-jc36-x5q9
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.1.2

## Details
Text-values were not properly escaped before printed in the version preview. This allowed XSS by authenticated users with access to the resources.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-w6j8-jc36-x5q9
- https://nvd.nist.gov/vuln/detail/CVE-2021-39166
- https://github.com/pimcore/pimcore/pull/10170
- https://github.com/pimcore/pimcore
