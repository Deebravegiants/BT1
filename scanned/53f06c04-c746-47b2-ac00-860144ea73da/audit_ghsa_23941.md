# [H] Improper Control of Generation of Code in doT

## Summary
Severity: High
Advisory: GHSA-297x-8xj4-vcxv
CVE: CVE-2020-8141
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-297x-8xj4-vcxv
Type: github-advisory

## Affected
- npm: `dot` — affected >=0 <1.1.3

## Details
The dot package v1.1.2 uses Function() to compile templates. This can be exploited by the attacker if they can control the given template or if they can control the value set on Object.prototype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8141
- https://hackerone.com/reports/390929
