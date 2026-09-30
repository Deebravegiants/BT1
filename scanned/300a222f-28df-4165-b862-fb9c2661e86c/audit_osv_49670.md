# [C] CVE-2019-15505

## Summary
Severity: Critical
Advisory: CVE-2019-15505
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-23
Source: https://osv.dev/vulnerability/CVE-2019-15505
Type: osv

## Details
drivers/media/usb/dvb-usb/technisat-usb2.c in the Linux kernel through 5.2.9 has an out-of-bounds read via crafted USB device traffic (which may be remote via usbip or usbredir).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4JZ6AEUKFWBHQAROGMQARJ274PQP2QP/
- https://lore.kernel.org/linux-media/20190821104408.w7krumcglxo6fz5q%40gofer.mess.org/
- https://support.f5.com/csp/article/K28222050?utm_source=f5support&amp%3Butm_medium=RSS
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3RUDQJXRJQVGHCGR4YZWTQ3ECBI7TXH/
- https://lore.kernel.org/lkml/b9b256cb-95f2-5fa1-9956-5a602a017c11%40gmail.com/
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://usn.ubuntu.com/4157-1/
- https://usn.ubuntu.com/4163-1/
- https://seclists.org/bugtraq/2019/Nov/11
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://support.f5.com/csp/article/K28222050
- https://usn.ubuntu.com/4157-2/
- https://usn.ubuntu.com/4162-1/
- https://usn.ubuntu.com/4162-2/
- https://usn.ubuntu.com/4163-2/
- http://packetstormsecurity.com/files/155212/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://git.linuxtv.org/media_tree.git/commit/?id=0c4df39e504bf925ab666132ac3c98d6cbbe380b
