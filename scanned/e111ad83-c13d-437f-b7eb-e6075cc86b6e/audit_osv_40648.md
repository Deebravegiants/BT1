# [C] ProFTPD mod_sftp Heap Buffer Overflow via Unsigned Integer Underflow and Size Truncation

## Summary
Severity: Critical
Advisory: CVE-2026-53994
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-18
Source: https://osv.dev/vulnerability/CVE-2026-53994
Type: osv

## Details
ProFTPD mod_sftp contains a heap-based buffer overflow reachable by an authenticated SFTP user. The fxp_packet_read() function accepts the attacker-supplied 32-bit big-endian SFTP packet length without a minimum sanity check. A value of 0 causes an unsigned subtraction elsewhere in the read path to underflow to approximately 4 GB. That oversized request reaches the core memory allocator, where the rounded size is computed in size_t but passed to new_block() as a 32-bit int; the low 32 bits of 0x100000000 are 0, so new_block() returns a small (~512-byte) block while the caller is told it received ~4 GB. The subsequent fill loop then streams attacker-controlled bytes past the end of the 544-byte allocation, producing an attacker-controlled heap buffer overflow. An authenticated user can crash the per-connection ProFTPD session child on demand with a single malformed SFTP packet (packet_len=0 followed by a body greater than approximately 544 bytes), producing reliable authenticated remote denial of service. Depending on heap layout and adjacent allocations, heap metadata corruption and further consequences beyond denial of service may be possible, though only denial of service is demonstrated by the supplied proof of concept.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53994.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53994
- https://www.vulncheck.com/advisories/proftpd-mod-sftp-heap-buffer-overflow-via-unsigned-integer-underflow-and-size-truncation
- https://github.com/proftpd/proftpd/commit/7342836fa98e36209660a4c5805c801476f63936
- https://github.com/proftpd/proftpd
