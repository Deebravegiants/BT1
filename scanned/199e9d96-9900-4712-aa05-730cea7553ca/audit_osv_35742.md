# [M] Util-linux: util-linux: heap use-after-free in libblkid nested partition probing

## Summary
Severity: Medium
Advisory: CVE-2026-13595
CVSS: 6.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-13595
Type: osv

## Details
A flaw was found in the libblkid library of util-linux. During nested partition probing, the BSD, Minix, Solaris x86, and UnixWare partition probers cache a raw pointer to a parent partition entry in a dynamically allocated array. When subsequent partition additions cause the array to be reallocated, this pointer becomes stale, leading to a heap use-after-free read. An attacker who can present a crafted block device image (for example, via USB insertion or a loop-mounted disk image) can trigger this flaw without user interaction, as libblkid is invoked automatically by udev/udisks as root on block-device hot-plug events. This could lead to limited information disclosure or denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:26573
- https://access.redhat.com/security/cve/CVE-2026-13595
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13595.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13595
- https://bugzilla.redhat.com/show_bug.cgi?id=2494101
- https://github.com/util-linux/util-linux/commit/c0186f14fbdb02f64c8e0ba701ce727ea764ff4c
