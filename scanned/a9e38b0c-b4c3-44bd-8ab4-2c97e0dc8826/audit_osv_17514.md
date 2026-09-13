# [H] CVE-2020-15852

## Summary
Severity: High
Advisory: CVE-2020-15852
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-20
Source: https://osv.dev/vulnerability/CVE-2020-15852
Type: osv

## Details
An issue was discovered in the Linux kernel 5.5 through 5.7.9, as used in Xen through 4.13.x for x86 PV guests. An attacker may be granted the I/O port permissions of an unrelated task. This occurs because tss_invalidate_io_bitmap mishandling causes a loss of synchronization between the I/O bitmaps of TSS and Xen, aka CID-cadfad870154.

## References
- https://security.netapp.com/advisory/ntap-20200810-0001/
- http://www.openwall.com/lists/oss-security/2020/07/21/2
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cadfad870154e14f745ec845708bc17d166065f2
- https://github.com/torvalds/linux/commit/cadfad870154e14f745ec845708bc17d166065f2
- http://xenbits.xen.org/xsa/advisory-329.html
