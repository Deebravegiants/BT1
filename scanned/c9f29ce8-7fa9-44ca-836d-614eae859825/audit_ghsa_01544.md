# [C] XXE attack in Mapfish Print

## Summary
Severity: Critical
Advisory: GHSA-vjv6-gq77-3mjw
CVE: CVE-2020-15232
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-07-07
Source: https://github.com/advisories/GHSA-vjv6-gq77-3mjw
Type: github-advisory

## Affected
- Maven: `org.mapfish.print:print-lib` — affected >=3.0 <3.24
- Maven: `org.mapfish.print:print-servlet` — affected >=3.0 <3.24
- Maven: `org.mapfish.print:print-standalone` — affected >=3.0 <3.24

## Details
### Impact
A user can do to an XML External Entity (XXE) attack with the provided SDL style.

### Patches
Use version >= 3.24

### Workarounds
No

### References
* https://cwe.mitre.org/data/definitions/611.html
* https://github.com/mapfish/mapfish-print/pull/1397/commits/e1d0527d13db06b2b62ca7d6afb9e97dacd67a0e

### For more information
If you have any questions or comments about this advisory Comment the pull request: https://github.com/mapfish/mapfish-print/pull/1397

## References
- https://github.com/mapfish/mapfish-print/security/advisories/GHSA-vjv6-gq77-3mjw
- https://nvd.nist.gov/vuln/detail/CVE-2020-15232
- https://github.com/mapfish/mapfish-print/pull/1397
- https://github.com/mapfish/mapfish-print/pull/1397/commits/e1d0527d13db06b2b62ca7d6afb9e97dacd67a0e
- https://github.com/mapfish/mapfish-print
