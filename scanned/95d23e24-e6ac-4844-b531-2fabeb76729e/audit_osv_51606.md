# [H] CVE-2021-35039

## Summary
Severity: High
Advisory: CVE-2021-35039
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-07
Source: https://osv.dev/vulnerability/CVE-2021-35039
Type: osv

## Details
kernel/module.c in the Linux kernel before 5.12.14 mishandles Signature Verification, aka CID-0c18f29aae7c. Without CONFIG_MODULE_SIG, verification that a kernel module is signed, for loading via init_module, does not occur for a module.sig_enforce=1 command-line argument.

## References
- https://lists.debian.org/debian-lts-announce/2021/10/msg00010.html
- https://security.netapp.com/advisory/ntap-20210813-0004/
- https://www.openwall.com/lists/oss-security/2021/07/06/3
- http://www.openwall.com/lists/oss-security/2021/07/06/3
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.14
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=0c18f29aae7ce3dadd26d8ee3505d07cc982df75
- https://github.com/torvalds/linux/commit/0c18f29aae7ce3dadd26d8ee3505d07cc982df75
