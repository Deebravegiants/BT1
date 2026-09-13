# [M] CVE-2019-14973

## Summary
Severity: Medium
Advisory: CVE-2019-14973
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-14
Source: https://osv.dev/vulnerability/CVE-2019-14973
Type: osv

## Details
_TIFFCheckMalloc and _TIFFCheckRealloc in tif_aux.c in LibTIFF through 4.0.10 mishandle Integer Overflow checks because they rely on compiler behavior that is undefined by the applicable C standards. This can, for example, lead to an application crash.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/63BVT6N5KQPHWOWM4B3I7Z3ODBXUVNPS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ADNPG7JJTRRK22GUVTAFH3GJ6WGKUZJB/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00102.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00023.html
- http://packetstormsecurity.com/files/155095/Slackware-Security-Advisory-libtiff-Updates.html
- https://lists.debian.org/debian-lts-announce/2019/08/msg00031.html
- https://seclists.org/bugtraq/2019/Nov/5
- https://seclists.org/bugtraq/2020/Jan/32
- https://www.debian.org/security/2020/dsa-4608
- https://www.debian.org/security/2020/dsa-4670
- https://gitlab.com/libtiff/libtiff/merge_requests/90
