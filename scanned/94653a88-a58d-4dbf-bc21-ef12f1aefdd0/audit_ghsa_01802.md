# [M] A vulnerability in Atomix v3.1.5 allows attackers to cause a denial of service (DoS) via a Raft session flooding attack using Raft OpenSessionRequest messages.

## Summary
Severity: Medium
Advisory: GHSA-mf27-wg66-m8f5
CVE: CVE-2020-35210
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-17
Source: https://github.com/advisories/GHSA-mf27-wg66-m8f5
Type: github-advisory

## Affected
- Maven: `io.atomix:atomix` — affected >=0

## Details
A vulnerability in Atomix v3.1.5 allows attackers to cause a denial of service (DoS) via a Raft session flooding attack using Raft OpenSessionRequest messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35210
- https://docs.google.com/presentation/d/1eZznIciFI06_5UJrXvlLugH2-nmjfYpQO5NyNMc9RxU/edit?usp=sharing
- https://github.com/atomix/atomix
