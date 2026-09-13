# [M] CVE-2015-5160

## Summary
Severity: Medium
Advisory: CVE-2015-5160
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2015-5160
Type: osv

## Details
libvirt before 2.2 includes Ceph credentials on the qemu command line when using RADOS Block Device (aka RBD), which allows local users to obtain sensitive information via a process listing.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2577.html
- http://www.openwall.com/lists/oss-security/2017/07/21/3
- https://bugs.launchpad.net/ossn/+bug/1686743
- https://bugzilla.redhat.com/show_bug.cgi?id=1245647
- https://wiki.openstack.org/wiki/OSSN/OSSN-0079
- http://www.openwall.com/lists/oss-security/2017/07/21/3
- https://bugs.launchpad.net/ossn/+bug/1686743
- https://bugzilla.redhat.com/show_bug.cgi?id=1245647
