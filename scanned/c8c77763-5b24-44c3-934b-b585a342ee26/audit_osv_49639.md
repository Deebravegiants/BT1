# [C] CVE-2019-14897

## Summary
Severity: Critical
Advisory: CVE-2019-14897
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-29
Source: https://osv.dev/vulnerability/CVE-2019-14897
Type: osv

## Details
A stack-based buffer overflow was found in the Linux kernel, version kernel-2.6.32, in Marvell WiFi chip driver. An attacker is able to cause a denial of service (system crash) or, possibly execute arbitrary code, when a STA works in IBSS mode (allows connecting stations together without the use of an AP) and connects to another STA.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MN6MLCN7G7VFTSXSZYXKXEFCUMFBUAXQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D4ISVNIC44SOGXTUBCIZFSUNQJ5LRKNZ/
- http://packetstormsecurity.com/files/155879/Kernel-Live-Patch-Security-Notice-LSN-0061-1.html
- http://packetstormsecurity.com/files/156185/Kernel-Live-Patch-Security-Notice-LSN-0062-1.html
- https://usn.ubuntu.com/4225-2/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://usn.ubuntu.com/4227-1/
- https://usn.ubuntu.com/4227-2/
- https://usn.ubuntu.com/4228-1/
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4226-1/
- https://usn.ubuntu.com/4228-2/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14897
