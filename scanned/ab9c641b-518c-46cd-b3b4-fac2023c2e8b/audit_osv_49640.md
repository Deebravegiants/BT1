# [C] CVE-2019-14901

## Summary
Severity: Critical
Advisory: CVE-2019-14901
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-29
Source: https://osv.dev/vulnerability/CVE-2019-14901
Type: osv

## Details
A heap overflow flaw was found in the Linux kernel, all versions 3.x.x and 4.x.x before 4.18.0, in Marvell WiFi chip driver. The vulnerability allows a remote attacker to cause a system crash, resulting in a denial of service, or execute arbitrary code. The highest threat with this vulnerability is with the availability of the system. If code execution occurs, the code will run with the permissions of root. This will affect both confidentiality and integrity of files on the system.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D4ISVNIC44SOGXTUBCIZFSUNQJ5LRKNZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MN6MLCN7G7VFTSXSZYXKXEFCUMFBUAXQ/
- https://access.redhat.com/errata/RHSA-2020:0204
- https://usn.ubuntu.com/4226-1/
- https://usn.ubuntu.com/4227-1/
- https://access.redhat.com/errata/RHSA-2020:0328
- https://usn.ubuntu.com/4225-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- http://packetstormsecurity.com/files/156185/Kernel-Live-Patch-Security-Notice-LSN-0062-1.html
- https://access.redhat.com/errata/RHSA-2020:0374
- https://access.redhat.com/errata/RHSA-2020:0375
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://usn.ubuntu.com/4225-2/
- https://usn.ubuntu.com/4227-2/
- http://packetstormsecurity.com/files/155879/Kernel-Live-Patch-Security-Notice-LSN-0061-1.html
- https://access.redhat.com/errata/RHSA-2020:0339
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4228-1/
- https://usn.ubuntu.com/4228-2/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14901
