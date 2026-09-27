# [C] smb/client: fix out-of-bounds read in smb2_compound_op()

## Summary
Severity: Critical
Advisory: CVE-2026-46155
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46155
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.140, >=6.7.0 <6.12.88, >=6.9.0 <6.18.30, >=6.13.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb/client: fix out-of-bounds read in smb2_compound_op()

If a server sends a truncated response but a large OutputBufferLength, and
terminates the EA list early, check_wsl_eas() returns success without
validating that the entire OutputBufferLength fits within iov_len.

Then smb2_compound_op() does:
    memcpy(idata->wsl.eas, data[0], size[0]);

Where size[0] is OutputBufferLength. If iov_len is smaller than size[0],
memcpy can read beyond the end of the rsp_iov allocation and leak adjacent
kernel heap memory.

## References
- https://git.kernel.org/stable/c/512d33bc8ea4ea5c19728ee118715f4b1f4d1926
- https://git.kernel.org/stable/c/8d09328dfda089675e4c049f3f256064a1d1996b
- https://git.kernel.org/stable/c/9b3af35645ff9cd334edc130249f9a2fb2bea25f
- https://git.kernel.org/stable/c/a16f70a71be4b5a4eccf39a9bf09b47285f4cb7c
- https://git.kernel.org/stable/c/dffb44b2e06a2908e249f0f93156fc987eee1d1c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46155.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46155
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
