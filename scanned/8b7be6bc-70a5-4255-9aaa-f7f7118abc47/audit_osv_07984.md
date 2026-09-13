# [M] CVE-2016-0777

## Summary
Severity: Medium
Advisory: CVE-2016-0777
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-01-14
Source: https://osv.dev/vulnerability/CVE-2016-0777
Type: osv

## Details
The resend_bytes function in roaming_common.c in the client in OpenSSH 5.x, 6.x, and 7.x before 7.1p2 allows remote servers to obtain sensitive information from process memory by requesting transmission of an entire buffer, as demonstrated by reading a private key.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10734
- http://lists.apple.com/archives/security-announce/2016/Mar/msg00004.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176516.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175592.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175676.html
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
- http://www.openssh.com/txt/release-7.1p2
- http://www.openwall.com/lists/oss-security/2016/01/14/7
- http://www.oracle.com/technetwork/topics/security/bulletinoct2015-2511968.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
