# [M] libssh2 through 1.11.1, fixed in commit 2dae302, contains an out-of-bounds heap read vulnerability...

## Summary
Severity: Medium
Advisory: JLSEC-2026-659
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/JLSEC-2026-659
Type: osv

## Affected
- Julia: `LibSSH2_jll` — affected >=0 <1.11.102+0

## Details
libssh2 through 1.11.1, fixed in commit 2dae302, contains an out-of-bounds heap read vulnerability in the `sftp_symlink()` function in `src/sftp.c` that allows a malicious SSH server or man-in-the-middle attacker to disclose heap memory contents or cause a crash by sending a crafted `SSH_FXP_NAME` response. Attackers can supply a `link_len` value larger than the actual packet data in `SSH_FXP_NAME` responses for SFTP READLINK and REALPATH operations, triggering a heap buffer over-read of up to `target_len` minus one bytes due to the missing validation of available packet buffer size before the memcpy operation.

## References
- https://github.com/advisories/GHSA-3wqh-87fg-ffgg
- https://github.com/libssh2/libssh2/commit/2dae3024897e1898d389835151f4e9606227721d
- https://github.com/libssh2/libssh2/pull/1705
- https://github.com/libssh2/libssh2/pull/1717
- https://nvd.nist.gov/vuln/detail/CVE-2025-15661
- https://www.vulncheck.com/advisories/libssh2-heap-buffer-over-read-via-sftp-symlink-in-sftp-c
