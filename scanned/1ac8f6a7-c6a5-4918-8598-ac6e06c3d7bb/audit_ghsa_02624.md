# [H] Prototype Pollution in set-value

## Summary
Severity: High
Advisory: GHSA-4jqc-8m5r-9rpr
CVE: CVE-2021-23440
CWE: CWE-1321, CWE-843
Ecosystem: NuGet, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-09-13
Source: https://github.com/advisories/GHSA-4jqc-8m5r-9rpr
Type: github-advisory

## Affected
- npm: `set-value` — affected >=4.0.0 <4.0.1
- NuGet: `set-value-nuget` — affected >=0 <2.0.0
- npm: `set-value` — affected >=0 <2.0.1
- npm: `set-value` — affected >=3.0.0 <3.0.3

## Details
This affects the package `set-value`. A type confusion vulnerability can lead to a bypass of CVE-2019-10747 when the user-provided keys used in the path parameter are arrays.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23440
- https://github.com/jonschlinkert/set-value/pull/33
- https://github.com/jonschlinkert/set-value/pull/33/commits/383b72d47c74a55ae8b6e231da548f9280a4296a
- https://github.com/jonschlinkert/set-value/commit/09c4b108fea3c0260008590053ff13da64913245
- https://github.com/jonschlinkert/set-value/commit/7cf8073bb06bf0c15e08475f9f952823b4576452
- https://github.com/jonschlinkert/set-value/commit/cb12f14955dde6e61829d70d1851bfea6a3c31ad
- https://github.com/jonschlinkert/set-value
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1584212
- https://snyk.io/vuln/SNYK-JS-SETVALUE-1540541
- https://www.huntr.dev/bounties/2eae1159-01de-4f82-a177-7478a408c4a2
- https://www.oracle.com/security-alerts/cpujan2022.html
