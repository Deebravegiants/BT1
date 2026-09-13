# [M] JLSEC-2026-1263

## Summary
Severity: Medium
Advisory: JLSEC-2026-1263
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/JLSEC-2026-1263
Type: osv

## Affected
- Julia: `Libmount_jll` — affected unspecified
- Julia: `util_linux_jll` — affected unspecified

## Details
A flaw was found in the libblkid library of util-linux. During nested partition probing, the BSD, Minix, Solaris x86, and UnixWare partition probers cache a raw pointer to a parent partition entry in a dynamically allocated array. When subsequent partition additions cause the array to be reallocated, this pointer becomes stale, leading to a heap use-after-free read. An attacker who can present a crafted block device image (for example, via USB insertion or a loop-mounted disk image) can trigger this flaw without user interaction, as libblkid is invoked automatically by udev/udisks as root on block-device hot-plug events. This could lead to limited information disclosure or denial of service.

## References
- https://access.redhat.com/errata/RHSA-2026:26573
- https://access.redhat.com/security/cve/CVE-2026-13595
- https://bugzilla.redhat.com/show_bug.cgi?id=2494101
- https://github.com/util-linux/util-linux/commit/c0186f14fbdb02f64c8e0ba701ce727ea764ff4c
