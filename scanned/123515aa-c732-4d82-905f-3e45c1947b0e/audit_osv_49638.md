# [C] CVE-2019-14896

## Summary
Severity: Critical
Advisory: CVE-2019-14896
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-27
Source: https://osv.dev/vulnerability/CVE-2019-14896
Type: osv

## Details
A heap-based buffer overflow vulnerability was found in the Linux kernel, version kernel-2.6.32, in Marvell WiFi chip driver. A remote attacker could cause a denial of service (system crash) or, possibly execute arbitrary code, when the lbs_ibss_join_existing function is called after a STA connects to an AP.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D4ISVNIC44SOGXTUBCIZFSUNQJ5LRKNZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MN6MLCN7G7VFTSXSZYXKXEFCUMFBUAXQ/
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- http://packetstormsecurity.com/files/155879/Kernel-Live-Patch-Security-Notice-LSN-0061-1.html
- https://usn.ubuntu.com/4226-1/
- http://packetstormsecurity.com/files/156185/Kernel-Live-Patch-Security-Notice-LSN-0062-1.html
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4225-2/
- https://usn.ubuntu.com/4227-1/
- https://usn.ubuntu.com/4227-2/
- https://usn.ubuntu.com/4228-1/
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://usn.ubuntu.com/4228-2/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14896
