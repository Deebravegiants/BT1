# [C] libssh2 - Out-of-Bounds Write via Unchecked packet_length in transport.c

## Summary
Severity: Critical
Advisory: CVE-2026-55200
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-55200
Type: osv

## Details
libssh2 through 1.11.1, fixed in commit 7acf3df contains an out-of-bounds write vulnerability in ssh2_transport_read() that fails to enforce upper bounds on packet_length field. Remote attackers can send crafted SSH packets with excessively large packet_length values to corrupt heap memory and achieve remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55200.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55200
- https://www.vulncheck.com/advisories/libssh2-out-of-bounds-write-via-unchecked-packet-length-in-transport-c
- https://github.com/libssh2/libssh2/pull/2052
- https://github.com/libssh2/libssh2/commit/97acf3dfda80c91c3a8c9f2372546301d4a1a7a8
- https://github.com/libssh2/libssh2
- https://web.archive.org/web/20260623211210/https://github.com/bikini/exploitarium/tree/main/libssh2-cve-2026-55200-poc
