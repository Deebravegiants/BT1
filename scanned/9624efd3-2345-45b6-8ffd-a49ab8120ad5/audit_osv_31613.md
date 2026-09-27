# [M] libssh2 - Heap Buffer Over-read via sftp_symlink() in sftp.c

## Summary
Severity: Medium
Advisory: CVE-2025-15661
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2025-15661
Type: osv

## Details
libssh2 through 1.11.1, fixed in commit 2dae302, contains an out-of-bounds heap read vulnerability in the sftp_symlink() function in src/sftp.c that allows a malicious SSH server or man-in-the-middle attacker to disclose heap memory contents or cause a crash by sending a crafted SSH_FXP_NAME response. Attackers can supply a link_len value larger than the actual packet data in SSH_FXP_NAME responses for SFTP READLINK and REALPATH operations, triggering a heap buffer over-read of up to target_len minus one bytes due to the missing validation of available packet buffer size before the memcpy operation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15661.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-15661
- https://www.vulncheck.com/advisories/libssh2-heap-buffer-over-read-via-sftp-symlink-in-sftp-c
- https://github.com/libssh2/libssh2/pull/1705
- https://github.com/libssh2/libssh2/pull/1717
- https://github.com/libssh2/libssh2/commit/2dae3024897e1898d389835151f4e9606227721d
- https://github.com/libssh2/libssh2
