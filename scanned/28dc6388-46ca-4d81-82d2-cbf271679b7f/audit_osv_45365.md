# [C] libssh2 through 1.11.1, fixed in commit 5e47761, contains a double-free vulnerability in the...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1085
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/JLSEC-2026-1085
Type: osv

## Affected
- Julia: `LibSSH2_jll` — affected >=0 <1.11.104+0

## Details
libssh2 through 1.11.1, fixed in commit 5e47761, contains a double-free vulnerability in the `sftp_open()` function in `src/sftp.c` that allows a malicious SSH server to corrupt the heap of any authenticated client opening an SFTP session. When a server responds to `SSH_FXP_OPEN` with `SSH_FXP_STATUS` containing `FX_OK`, the response data buffer is freed, and if a subsequent `sftp_packet_require()` call returns a specific error such as `LIBSSH2_ERROR_CHANNEL_PACKET_EXCEEDED`, the same pointer is freed a second time, enabling tcache dup conditions on glibc systems that allow overlapping allocations and function pointer overwrites.

## References
- https://github.com/advisories/GHSA-83r8-6c29-8gwr
- https://github.com/libssh2/libssh2/commit/5e4776146552d898b9c0e1b313cd093fa8dc92d0
- https://github.com/libssh2/libssh2/pull/2180
- https://nvd.nist.gov/vuln/detail/CVE-2026-66032
- https://www.vulncheck.com/advisories/libssh2-double-free-heap-corruption-via-sftp-open
