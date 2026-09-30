# [H] fbdev: Fix vmalloc out-of-bounds write in fast_imageblit

## Summary
Severity: High
Advisory: CVE-2025-38685
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38685
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: Fix vmalloc out-of-bounds write in fast_imageblit

This issue triggers when a userspace program does an ioctl
FBIOPUT_CON2FBMAP by passing console number and frame buffer number.
Ideally this maps console to frame buffer and updates the screen if
console is visible.

As part of mapping it has to do resize of console according to frame
buffer info. if this resize fails and returns from vc_do_resize() and
continues further. At this point console and new frame buffer are mapped
and sets display vars. Despite failure still it continue to proceed
updating the screen at later stages where vc_data is related to previous
frame buffer and frame buffer info and display vars are mapped to new
frame buffer and eventully leading to out-of-bounds write in
fast_imageblit(). This bheviour is excepted only when fg_console is
equal to requested console which is a visible console and updates screen
with invalid struct references in fbcon_putcs().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/078e62bffca4b7e72e8f3550eb063ab981c36c7a
- https://git.kernel.org/stable/c/27b118aebdd84161c8ff5ce49d9d536f2af10754
- https://git.kernel.org/stable/c/4c4d7ddaf1d43780b106bedc692679f965dc5a3a
- https://git.kernel.org/stable/c/56701bf9eeb63219e378cb7fcbd066ea4eaeeb50
- https://git.kernel.org/stable/c/af0db3c1f898144846d4c172531a199bb3ca375d
- https://git.kernel.org/stable/c/cfec17721265e72e50cc69c6004fe3475cd38df2
- https://git.kernel.org/stable/c/ed9b8e5016230868c8d813d9179523f729fec8c6
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38685.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38685
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
