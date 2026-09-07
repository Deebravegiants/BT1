# [M] @builder.io/qwik vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-hm7f-rq7q-j9xp
CVE: CVE-2023-0410
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-hm7f-rq7q-j9xp
Type: github-advisory

## Affected
- npm: `@builder.io/qwik` — affected >=0 <0.16.2

## Details
@builder.io/qwik prior to version 0.16.2 is vulnerable to cross-site scripting due to attribute names and the class attribute values not being properly handled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0410
- https://github.com/builderio/qwik/commit/4b2f89dbbd2bc0a2c92eae1a49bdd186e589151a
- https://github.com/BuilderIO/qwik
- https://huntr.dev/bounties/2da583f0-7f66-4ba7-9bed-8e7229aa578e
