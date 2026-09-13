# [H] CVE-2019-2215

## Summary
Severity: High
Advisory: CVE-2019-2215
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-11
Source: https://osv.dev/vulnerability/CVE-2019-2215
Type: osv

## Details
A use-after-free in binder.c allows an elevation of privilege from an application to the Linux Kernel. No user interaction is required to exploit this vulnerability, however exploitation does require either the installation of a malicious local application or a separate vulnerability in a network facing application.Product: AndroidAndroid ID: A-141720095

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-2215
- http://seclists.org/fulldisclosure/2019/Oct/38
- http://www.huawei.com/en/psirt/security-advisories/huawei-sa-20191030-01-binder-en
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://security.netapp.com/advisory/ntap-20191031-0005/
- https://usn.ubuntu.com/4186-1/
- https://source.android.com/security/bulletin/2019-10-01
- http://packetstormsecurity.com/files/155212/Slackware-Security-Advisory-Slackware-14.2-kernel-Updates.html
- https://seclists.org/bugtraq/2019/Nov/11
- http://packetstormsecurity.com/files/154911/Android-Binder-Use-After-Free.html
- http://packetstormsecurity.com/files/156495/Android-Binder-Use-After-Free.html
