# [C] Prototype Pollution in async merge-object

## Summary
Severity: Critical
Advisory: GHSA-fp82-2h99-3fpp
CVE: CVE-2018-3753
CWE: CWE-1321, CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-09-18
Source: https://github.com/advisories/GHSA-fp82-2h99-3fpp
Type: github-advisory

## Affected
- npm: `merge-object` — affected >=0

## Details
The utilities function in all versions of the merge-object node module can be tricked into modifying the prototype of Object when the attacker can control part of the structure passed to this function. This can let an attacker add or modify existing properties that will exist on all objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3753
- https://hackerone.com/reports/310706
