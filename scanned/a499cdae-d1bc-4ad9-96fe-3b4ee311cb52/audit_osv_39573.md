# [C] smb/client: fix out-of-bounds read in symlink_data()

## Summary
Severity: Critical
Advisory: CVE-2026-46185
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46185
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb/client: fix out-of-bounds read in symlink_data()

Since smb2_check_message() returns success without length validation for
the symlink error response, in symlink_data() it is possible for
iov->iov_len to be smaller than sizeof(struct smb2_err_rsp). If the buffer
only contains the base SMB2 header (64 bytes), accessing
err->ErrorContextCount (at offset 66) or err->ByteCount later in
symlink_data() will cause an out-of-bounds read.

## References
- https://git.kernel.org/stable/c/15dc0a4de743a1aaa7b859b3aea79f08c695396c
- https://git.kernel.org/stable/c/2be11faf79e49fb8250a181ff0b4d2b2f084af83
- https://git.kernel.org/stable/c/b8c8a704f0bc133deb171f6aeb6f3a684203e212
- https://git.kernel.org/stable/c/b9561402489d41149f63e001a74384863b7b30a6
- https://git.kernel.org/stable/c/d62b8d236fab503c6fec1d3e9a38bea71feaca20
- https://git.kernel.org/stable/c/ef6495d4df6e7af8f3de67e65150881c880f696c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46185.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46185
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
