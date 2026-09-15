# [M] Malicious Atomix node queries expose sensitive information

## Summary
Severity: Medium
Advisory: GHSA-g7p8-r2ch-4rmf
CVE: CVE-2020-35215
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-12-17
Source: https://github.com/advisories/GHSA-g7p8-r2ch-4rmf
Type: github-advisory

## Affected
- Maven: `io.atomix:atomix` — affected >=0

## Details
An issue in Atomix v3.1.5 allows attackers to access sensitive information when a malicious Atomix node queries distributed variable primitives which contain the entire primitive lists that ONOS nodes use to share important states.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35215
- https://docs.google.com/presentation/d/1pRRLfdSUqUZ688CZ9e9AyceuXPGp9oyGj7j4bdSsBcw/edit?usp=sharing
- https://github.com/atomix/atomix
