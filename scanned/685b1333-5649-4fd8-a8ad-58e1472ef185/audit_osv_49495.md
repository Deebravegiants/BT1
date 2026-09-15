# [M] CVE-2019-13631

## Summary
Severity: Medium
Advisory: CVE-2019-13631
CVSS: 6.8 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-13631
Type: osv

## Details
In parse_hid_report_descriptor in drivers/input/tablet/gtco.c in the Linux kernel through 5.2.1, a malicious USB device can send an HID report that triggers an out-of-bounds write during generation of debugging messages.

## References
- https://usn.ubuntu.com/4147-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00056.html
- http://packetstormsecurity.com/files/154059/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TUXTJSLIQBOJTQDMTUQTQKUWWAJLFVEY/
- https://seclists.org/bugtraq/2019/Aug/18
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KQ5BQKTI24DPSVKPOIMMGDTFKCF6ASXT/
- https://seclists.org/bugtraq/2019/Aug/13
- https://usn.ubuntu.com/4115-1/
- https://usn.ubuntu.com/4118-1/
- https://lists.debian.org/debian-lts-announce/2019/08/msg00016.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00017.html
- https://seclists.org/bugtraq/2019/Aug/26
- https://usn.ubuntu.com/4145-1/
- http://www.securityfocus.com/bid/109291
- https://www.debian.org/security/2019/dsa-4495
- https://www.debian.org/security/2019/dsa-4497
- https://security.netapp.com/advisory/ntap-20190806-0001/
- https://patchwork.kernel.org/patch/11040813/
