# [M] CVE-2025-24946

## Summary
Severity: Medium
Advisory: CVE-2025-24946
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-02-20
Source: https://osv.dev/vulnerability/CVE-2025-24946
Type: osv

## Details
The hash table used to manage connections in picoquic before b80fd3f uses a weak hash function, allowing remote attackers to cause a considerable CPU load on the server (a Hash DoS attack) by initiating connections with colliding Source Connection IDs (SCIDs).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24946.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-24946
- https://github.com/private-octopus/picoquic/commit/b80fd3f5903279ae3e7714ee4109363d9ab4491a
- https://github.com/ncc-pbottine/QUIC-Hash-Dos-Advisory
