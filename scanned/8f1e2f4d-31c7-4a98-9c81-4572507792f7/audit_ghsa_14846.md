# [M] Weak encryption in Ninja Core

## Summary
Severity: Medium
Advisory: GHSA-92wp-jghr-hh87
CVE: CVE-2024-36823
CWE: CWE-326
Ecosystem: Maven
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-92wp-jghr-hh87
Type: github-advisory

## Affected
- Maven: `org.ninjaframework:ninja-core` — affected 7.0.0

## Details
The encrypt() function of Ninja Core v7.0.0 was discovered to use a weak cryptographic algorithm, leading to a possible leakage of sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36823
- https://github.com/ninjaframework/ninja/issues/759
- https://github.com/ninjaframework/ninja
