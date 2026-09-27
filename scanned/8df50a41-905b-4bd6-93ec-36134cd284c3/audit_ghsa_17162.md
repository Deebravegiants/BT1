# [M] quiche vulnerable to unlimited resource allocation by QUIC CRYPTO frames flooding

## Summary
Severity: Medium
Advisory: GHSA-78wx-jg4j-5j6g
CVE: CVE-2024-1765
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-13
Source: https://github.com/advisories/GHSA-78wx-jg4j-5j6g
Type: github-advisory

## Affected
- crates.io: `quiche` — affected >=0 <0.19.2
- crates.io: `quiche` — affected >=0.20.0 <0.20.1

## Details
### Impact

Cloudflare Quiche (through version 0.19.1/0.20.0) was affected by an unlimited resource allocation vulnerability causing rapid increase of memory usage of the system running quiche server or client.

A remote attacker could take advantage of this vulnerability by repeatedly sending an unlimited number of 1-RTT CRYPTO frames after previously completing the QUIC handshake.
Exploitation was possible for the duration of the connection which could be extended by the attacker.

### Patches

Quiche 0.19.2 and 0.20.1 are the earliest versions containing the fix for this issue.

## References
- https://github.com/cloudflare/quiche/security/advisories/GHSA-78wx-jg4j-5j6g
- https://nvd.nist.gov/vuln/detail/CVE-2024-1765
- https://github.com/cloudflare/quiche/commit/1017466c143fc93a82b286a1ba35e53334cdf8e2
- https://github.com/cloudflare/quiche/commit/11dbf5461ab657bbc02e466d719070124b27ef3c
- https://github.com/cloudflare/quiche
- https://github.com/cloudflare/quiche/releases/tag/0.19.2
- https://github.com/cloudflare/quiche/releases/tag/0.20.1
