# [M] CVE-2017-11334

## Summary
Severity: Medium
Advisory: CVE-2017-11334
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-02
Source: https://osv.dev/vulnerability/CVE-2017-11334
Type: osv

## Details
The address_space_write_continue function in exec.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (out-of-bounds access and guest instance crash) by leveraging use of qemu_map_ram_ptr to access guest ram block area.

## References
- http://www.debian.org/security/2017/dsa-3925
- http://www.securityfocus.com/bid/99895
- https://access.redhat.com/errata/RHSA-2017:3369
- https://access.redhat.com/errata/RHSA-2017:3466
- https://access.redhat.com/errata/RHSA-2017:3470
- https://access.redhat.com/errata/RHSA-2017:3471
- https://access.redhat.com/errata/RHSA-2017:3472
- https://access.redhat.com/errata/RHSA-2017:3473
- https://access.redhat.com/errata/RHSA-2017:3474
- https://usn.ubuntu.com/3575-1/
- http://www.openwall.com/lists/oss-security/2017/07/17/4
- https://bugzilla.redhat.com/show_bug.cgi?id=1471638
- https://lists.gnu.org/archive/html/qemu-devel/2017-07/msg03775.html
