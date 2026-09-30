# [M] CVE-2019-3840

## Summary
Severity: Medium
Advisory: CVE-2019-3840
CVSS: 6.3 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/CVE-2019-3840
Type: osv

## Details
A NULL pointer dereference flaw was discovered in libvirt before version 5.0.0 in the way it gets interface information through the QEMU agent. An attacker in a guest VM can use this flaw to crash libvirtd and cause a denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TZRP2BRMI4RYFRPNFTTIAAUOGVN2ORP7/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00101.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00105.html
- https://access.redhat.com/errata/RHSA-2019:2294
- https://bugzilla.redhat.com/show_bug.cgi?id=1663051
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3840
- https://www.redhat.com/archives/libvir-list/2019-January/msg00241.html
