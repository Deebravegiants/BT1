# [H] clone_private_mnt(): make sure that caller has CAP_SYS_ADMIN in the right userns

## Summary
Severity: High
Advisory: CVE-2025-38499
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-38499
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.190, >=5.16.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

clone_private_mnt(): make sure that caller has CAP_SYS_ADMIN in the right userns

What we want is to verify there is that clone won't expose something
hidden by a mount we wouldn't be able to undo.  "Wouldn't be able to undo"
may be a result of MNT_LOCKED on a child, but it may also come from
lacking admin rights in the userns of the namespace mount belongs to.

clone_private_mnt() checks the former, but not the latter.

There's a number of rather confusing CAP_SYS_ADMIN checks in various
userns during the mount, especially with the new mount API; they serve
different purposes and in case of clone_private_mnt() they usually,
but not always end up covering the missing check mentioned above.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/36fecd740de2d542d2091d65d36554ee2bcf9c65
- https://git.kernel.org/stable/c/38628ae06e2a37770cd794802a3f1310cf9846e3
- https://git.kernel.org/stable/c/c28f922c9dcee0e4876a2c095939d77fe7e15116
- https://git.kernel.org/stable/c/d717325b5ecf2a40daca85c61923e17f32306179
- https://git.kernel.org/stable/c/dc6a664089f10eab0fb36b6e4f705022210191d2
- https://git.kernel.org/stable/c/e77078e52fbf018ab986efb3c79065ab35025607
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38499.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38499
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
