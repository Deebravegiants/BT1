# [C] CVE-2019-14895

## Summary
Severity: Critical
Advisory: CVE-2019-14895
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-29
Source: https://osv.dev/vulnerability/CVE-2019-14895
Type: osv

## Details
A heap-based buffer overflow was discovered in the Linux kernel, all versions 3.x.x and 4.x.x before 4.18.0, in Marvell WiFi chip driver. The flaw could occur when the station attempts a connection negotiation during the handling of the remote devices country settings. This could allow the remote device to cause a denial of service (system crash) or possibly execute arbitrary code.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MN6MLCN7G7VFTSXSZYXKXEFCUMFBUAXQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D4ISVNIC44SOGXTUBCIZFSUNQJ5LRKNZ/
- http://packetstormsecurity.com/files/155879/Kernel-Live-Patch-Security-Notice-LSN-0061-1.html
- https://access.redhat.com/errata/RHSA-2020:0339
- https://access.redhat.com/errata/RHSA-2020:0374
- https://access.redhat.com/errata/RHSA-2020:0592
- https://access.redhat.com/errata/RHSA-2020:0609
- https://usn.ubuntu.com/4227-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- http://packetstormsecurity.com/files/156185/Kernel-Live-Patch-Security-Notice-LSN-0062-1.html
- https://access.redhat.com/errata/RHSA-2020:0328
- https://access.redhat.com/errata/RHSA-2020:0375
- https://access.redhat.com/errata/RHSA-2020:0664
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4226-1/
- https://access.redhat.com/errata/RHSA-2020:0653
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4225-2/
- https://usn.ubuntu.com/4227-2/
- https://usn.ubuntu.com/4228-1/
