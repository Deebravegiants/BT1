# [M] smb: Initialize cfid->tcon before performing network ops

## Summary
Severity: Medium
Advisory: CVE-2024-56729
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56729
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: Initialize cfid->tcon before performing network ops

Avoid leaking a tcon ref when a lease break races with opening the
cached directory. Processing the leak break might take a reference to
the tcon in cached_dir_lease_break() and then fail to release the ref in
cached_dir_offload_close, since cfid->tcon is still NULL.

## References
- https://git.kernel.org/stable/c/1b9ab6b648f89441c8a13cb3fd8ca83ffebc5262
- https://git.kernel.org/stable/c/4b216c8f9c7d84ef7de33ca60b97e08e03ef3292
- https://git.kernel.org/stable/c/625e2357c8fcfae6e66dcc667dc656fe390bab15
- https://git.kernel.org/stable/c/c353ee4fb119a2582d0e011f66a76a38f5cf984d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56729.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56729
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
