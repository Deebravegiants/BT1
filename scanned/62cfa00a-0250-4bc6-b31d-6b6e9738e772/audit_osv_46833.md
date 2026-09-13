# [H] CVE-2015-5260

## Summary
Severity: High
Advisory: CVE-2015-5260
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-07
Source: https://osv.dev/vulnerability/CVE-2015-5260
Type: osv

## Details
Heap-based buffer overflow in SPICE before 0.12.6 allows guest OS users to cause a denial of service (heap-based memory corruption and QEMU-KVM crash) or possibly execute arbitrary code on the host via QXL commands related to the surface_id parameter.

## References
- http://rhn.redhat.com/errata/RHSA-2015-1889.html
- http://rhn.redhat.com/errata/RHSA-2015-1890.html
- http://www.debian.org/security/2015/dsa-3371
- http://www.ubuntu.com/usn/USN-2766-1
- https://security.gentoo.org/glsa/201606-05
- https://bugzilla.redhat.com/show_bug.cgi?id=1260822
- http://lists.freedesktop.org/archives/spice-devel/2015-October/022191.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2015-2719645.html
- http://www.securityfocus.com/bid/77019
- http://www.securitytracker.com/id/1033753
