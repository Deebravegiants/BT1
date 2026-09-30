# [H] Improper exception handling in Aedes

## Summary
Severity: High
Advisory: GHSA-gh78-48h3-frjq
CVE: CVE-2020-13410
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-gh78-48h3-frjq
Type: github-advisory

## Affected
- npm: `aedes` — affected >=0 <0.42.1

## Details
An issue was discovered in MoscaJS Aedes 0.42.0 and fixed in 0.42.1. lib/write.js does not properly consider exceptions during the writing of an invalid packet to a stream.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13410
- https://github.com/moscajs/aedes/pull/493
- https://github.com/moscajs/aedes/commit/8d34ee5819cfc983d57e49b45d8c5ef70a76d79b
- https://payatu.com/advisory/dos-in-aedes-mqtt-broker
