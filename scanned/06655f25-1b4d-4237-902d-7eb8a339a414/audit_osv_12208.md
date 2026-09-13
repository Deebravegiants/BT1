# [M] CVE-2018-10908

## Summary
Severity: Medium
Advisory: CVE-2018-10908
CVSS: 6.3 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:N/I:N/A:H)
Published: 2018-08-09
Source: https://osv.dev/vulnerability/CVE-2018-10908
Type: osv

## Details
It was found that vdsm before version 4.20.37 invokes qemu-img on untrusted inputs without limiting resources. By uploading a specially crafted image, an attacker could cause the qemu-img process to consume unbounded amounts of memory of CPU time, causing a denial of service condition that could potentially impact other users of the host.

## References
- http://lists.nongnu.org/archive/html/qemu-block/2018-07/msg00488.html
- https://access.redhat.com/errata/RHEA-2018:2624
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10908
- https://gerrit.ovirt.org/#/c/93195/
