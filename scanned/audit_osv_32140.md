# [M] CVE-2025-24947

## Summary
Severity: Medium
Advisory: CVE-2025-24947
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-02-20
Source: https://osv.dev/vulnerability/CVE-2025-24947
Type: osv

## Details
A hash collision vulnerability (in the hash table used to manage connections) in LSQUIC (aka LiteSpeed QUIC) before 4.2.0 allows remote attackers to cause a considerable CPU load on the server (a Hash DoS attack) by initiating connections with colliding Source Connection IDs (SCIDs). This is caused by XXH32 usage.

## References
- https://github.com/litespeedtech/lsquic/releases/tag/v4.2.0
- https://xxhash.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24947.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-24947
- https://github.com/ncc-pbottine/QUIC-Hash-Dos-Advisory
