# [C] CVE-2019-11036

## Summary
Severity: Critical
Advisory: CVE-2019-11036
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-05-03
Source: https://osv.dev/vulnerability/CVE-2019-11036
Type: osv

## Details
When processing certain files, PHP EXIF extension in versions 7.1.x below 7.1.29, 7.2.x below 7.2.18 and 7.3.x below 7.3.5 can be caused to read past allocated buffer in exif_process_IFD_TAG function. This may lead to information disclosure or crash.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2NFXYNCXZCPYT7ZN4ZLI5EPQQW44FRRO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3BY2XUUAN277LS7HKAOGL4DVGAELOJV3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WN2HLPGEZEF4MFM5YC5FILZB5QEQFP3A/
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00044.html
- http://www.securityfocus.com/bid/108177
- https://access.redhat.com/errata/RHSA-2019:2519
- https://access.redhat.com/errata/RHSA-2019:3299
- https://bugs.php.net/bug.php?id=77950
- https://lists.debian.org/debian-lts-announce/2019/05/msg00035.html
- https://seclists.org/bugtraq/2019/Sep/35
- https://seclists.org/bugtraq/2019/Sep/38
- https://security.netapp.com/advisory/ntap-20190517-0003/
- https://usn.ubuntu.com/3566-2/
- https://usn.ubuntu.com/4009-1/
- https://www.debian.org/security/2019/dsa-4527
- https://www.debian.org/security/2019/dsa-4529
