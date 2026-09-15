# [C] Improper Input Validation in Deap

## Summary
Severity: Critical
Advisory: GHSA-xg47-r67p-vhv5
CVE: CVE-2018-3749
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xg47-r67p-vhv5
Type: github-advisory

## Affected
- npm: `deap` — affected >=0 <1.0.1

## Details
The utilities function in all versions < 1.0.1 of the deap node module can be tricked into modifying the prototype of Object when the attacker can control part of the structure passed to this function. This can let an attacker add or modify existing properties that will exist on all objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3749
- https://github.com/selfcontained/deap/commit/ed27b7e890bdd616e1ee931ea1c64228e2b52a71
- https://hackerone.com/reports/310446
- https://github.com/selfcontained/deap
