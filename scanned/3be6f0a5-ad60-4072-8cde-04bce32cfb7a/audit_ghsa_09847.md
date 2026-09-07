# [M] Replicator deserializes untrusted user input

## Summary
Severity: Medium
Advisory: GHSA-2gmp-34j9-fqjm
CVE: CVE-2026-2265
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-2gmp-34j9-fqjm
Type: github-advisory

## Affected
- npm: `replicator` — affected >=0

## Details
An unauthenticated Remote Code Execution (RCE) vulnerability exists in applications that use the Replicator node package manager (npm) version 1.0.5 to deserialize untrusted user input and execute the resulting object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2265
- https://github.com/inikulin/replicator/pull/19
- https://github.com/inikulin/replicator
- https://morielharush.github.io/2026/03/31/cve-2026-2265-replicator-deserialization-of-untrusted-data
