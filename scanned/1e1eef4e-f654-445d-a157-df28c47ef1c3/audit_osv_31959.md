# [H] ksmbd: fix overflow in dacloffset bounds check

## Summary
Severity: High
Advisory: CVE-2025-22039
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22039
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix overflow in dacloffset bounds check

The dacloffset field was originally typed as int and used in an
unchecked addition, which could overflow and bypass the existing
bounds check in both smb_check_perm_dacl() and smb_inherit_dacl().

This could result in out-of-bounds memory access and a kernel crash
when dereferencing the DACL pointer.

This patch converts dacloffset to unsigned int and uses
check_add_overflow() to validate access to the DACL.

## References
- https://git.kernel.org/stable/c/443b373a4df5a2cb9f7b8c4658b2afedeb16397f
- https://git.kernel.org/stable/c/6a9cd9ff0fa2bcc30b2bfb8bdb161eb20e44b9dc
- https://git.kernel.org/stable/c/6b8d379048b168a0dff5ab1acb975b933f368514
- https://git.kernel.org/stable/c/beff0bc9d69bc8e733f9bca28e2d3df5b3e10e42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22039.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22039
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
