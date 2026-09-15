# [C] smb: client: fix potential UAF and double free in smb2_open_file()

## Summary
Severity: Critical
Advisory: CVE-2026-45972
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45972
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix potential UAF and double free in smb2_open_file()

Zero out @err_iov and @err_buftype before retrying SMB2_open() to
prevent an UAF bug if @data != NULL, otherwise a double free.

## References
- https://git.kernel.org/stable/c/4d339b219004869e96c4ce56b8891f83a38da4c0
- https://git.kernel.org/stable/c/639deb962986ef2f5e2a6d5a600c66f922471e81
- https://git.kernel.org/stable/c/7425453ea16dbc3bbb0f6cac4d60b537e5e4d151
- https://git.kernel.org/stable/c/96e53bb3ee2f354cf6b4ab07bcc56e500f8b3f74
- https://git.kernel.org/stable/c/e66dcf7bb9c4df5582c82bc3582725abcbfbea73
- https://git.kernel.org/stable/c/ebbbc4bfad4cb355d17c671223d0814ee3ef4eda
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-45972.json
- https://access.redhat.com/security/cve/CVE-2026-45972
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45972.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45972
- https://bugzilla.redhat.com/show_bug.cgi?id=2481973
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
