# [H] CVE-2016-0778

## Summary
Severity: High
Advisory: CVE-2016-0778
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-01-14
Source: https://osv.dev/vulnerability/CVE-2016-0778
Type: osv

## Details
The (1) roaming_read and (2) roaming_write functions in roaming_common.c in the client in OpenSSH 5.x, 6.x, and 7.x before 7.1p2, when certain proxy and forward options are enabled, do not properly maintain connection file descriptors, which allows remote servers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact by requesting many forwardings.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10734
- http://lists.apple.com/archives/security-announce/2016/Mar/msg00004.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176516.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/176349.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00013.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00014.html
- http://packetstormsecurity.com/files/135273/Qualys-Security-Advisory-OpenSSH-Overflow-Leak.html
- http://seclists.org/fulldisclosure/2016/Jan/44
- http://www.debian.org/security/2016/dsa-3446
- http://www.oracle.com/technetwork/topics/security/bulletinoct2015-2511968.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/archive/1/537295/100/0/threaded
- http://www.securityfocus.com/bid/80698
- http://www.securitytracker.com/id/1034671
- http://www.ubuntu.com/usn/USN-2869-1
