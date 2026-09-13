# [C] Access of Resource Using Incompatible Type in Hermes

## Summary
Severity: Critical
Advisory: GHSA-7mhc-prgv-r3q4
CVE: CVE-2021-24044
CWE: CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-16
Source: https://github.com/advisories/GHSA-7mhc-prgv-r3q4
Type: github-advisory

## Affected
- npm: `hermes-engine` — affected >=0 <0.10.0

## Details
By passing invalid javascript code where await and yield were called upon non-async and non-generator getter/setter functions, Hermes would invoke generator functions and error out on invalid await/yield positions. This could result in segmentation fault as a consequence of type confusion error, with a low chance of RCE. This issue affects Hermes versions prior to v0.10.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-24044
- https://github.com/facebook/hermes
- https://www.facebook.com/security/advisories/cve-2021-24044
