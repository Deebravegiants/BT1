# [M] CVE-2014-3672

## Summary
Severity: Medium
Advisory: CVE-2014-3672
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-05-25
Source: https://osv.dev/vulnerability/CVE-2014-3672
Type: osv

## Details
The qemu implementation in libvirt before 1.3.0 and Xen allows local guest OS users to cause a denial of service (host disk consumption) by writing to stdout or stderr.

## References
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securitytracker.com/id/1035945
- http://xenbits.xen.org/xsa/advisory-180.html
- https://libvirt.org/news-2015.html
- http://www.openwall.com/lists/oss-security/2016/05/24/5
- https://libvirt.org/git/?p=libvirt.git%3Ba=commit%3Bh=0d968ad715475a1660779bcdd2c5b38ad63db4cf
