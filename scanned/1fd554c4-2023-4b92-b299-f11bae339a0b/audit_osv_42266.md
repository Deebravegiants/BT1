# [C] libssh2 Heap Buffer Overflow via ETM Cipher Negotiation

## Summary
Severity: Critical
Advisory: CVE-2026-66035
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66035
Type: osv

## Details
libssh2 through 1.11.1, fixed in commit 42e33d8, contains a pre-authentication heap buffer overflow vulnerability that allows a malicious SSH server to corrupt heap metadata in any connecting client by sending a packet with a packet_length smaller than the cipher's block size during Encrypt-then-MAC cipher negotiation. In the fullpacket() function in src/transport.c, the ETM path allocates a buffer of packet_length bytes but copies blocksize minus one bytes via memcpy, causing an overflow that on 32-bit glibc writes attacker-controlled bytes into an adjacent chunk's SIZE field, enabling tcache bin confusion, overlapping live objects, and function pointer overwrite during the session handshake before authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66035.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66035
- https://www.vulncheck.com/advisories/libssh2-heap-buffer-overflow-via-etm-cipher-negotiation
- https://github.com/libssh2/libssh2/commit/42e33d81577ed4b95d4b4f6f845e5ee8efe5eeb4
- https://github.com/libssh2/libssh2/pull/2198
- https://github.com/libssh2/libssh2
