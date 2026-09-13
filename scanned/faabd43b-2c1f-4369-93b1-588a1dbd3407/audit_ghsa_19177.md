# [M] Kwik hash collision vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9f57-9rhg-4hvm
CVE: CVE-2025-23020
CWE: CWE-407
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-02-20
Source: https://github.com/advisories/GHSA-9f57-9rhg-4hvm
Type: github-advisory

## Affected
- Maven: `tech.kwik:kwik` — affected >=0 <0.10.1

## Details
An issue was discovered in Kwik before 0.10.1. A hash collision vulnerability (in the hash table used to manage connections) allows remote attackers to cause a considerable CPU load on the server (a Hash DoS attack) by initiating connections with colliding Source Connection IDs (SCIDs).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-23020
- https://github.com/ptrd/kwik/commit/b0733d72bad76bc5d8df2f4a7792ebb2539ebdc8
- https://github.com/ncc-pbottine/QUIC-Hash-Dos-Advisory
- https://github.com/ptrd/kwik
- https://github.com/ptrd/kwik/releases/tag/v0.10.1
