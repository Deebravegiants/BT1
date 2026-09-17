# [M] Netty QUIC hash collision DoS attack

## Summary
Severity: Medium
Advisory: GHSA-hqqc-jr88-p6x2
CVE: CVE-2025-29908
CWE: CWE-407
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-03-31
Source: https://github.com/advisories/GHSA-hqqc-jr88-p6x2
Type: github-advisory

## Affected
- Maven: `io.netty.incubator:netty-incubator-codec-quic` — affected >=0 <0.0.71.Final

## Details
An issue was discovered in the codec. A hash collision vulnerability (in the hash map used to manage connections) allows remote attackers to cause a considerable CPU load on the server (a Hash DoS attack) by initiating connections with colliding Source Connection IDs (SCIDs).

See https://github.com/ncc-pbottine/QUIC-Hash-Dos-Advisory

## References
- https://github.com/netty/netty-incubator-codec-quic/security/advisories/GHSA-hqqc-jr88-p6x2
- https://nvd.nist.gov/vuln/detail/CVE-2025-29908
- https://github.com/netty/netty-incubator-codec-quic/commit/e059bd9b78723f8b035e0c547e42ce263f03461c
- https://github.com/ncc-pbottine/QUIC-Hash-Dos-Advisory
- https://github.com/netty/netty-incubator-codec-quic
