# [C] CVE-2016-1908

## Summary
Severity: Critical
Advisory: CVE-2016-1908
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-11
Source: https://osv.dev/vulnerability/CVE-2016-1908
Type: osv

## Details
The client in OpenSSH before 7.2 mishandles failed cookie generation for untrusted X11 forwarding and relies on the local X11 server for access-control decisions, which allows remote X11 clients to trigger a fallback and obtain trusted X11 forwarding privileges by leveraging configuration issues on this X11 server, as demonstrated by lack of the SECURITY extension on this X11 server.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- http://www.securitytracker.com/id/1034705
- https://lists.debian.org/debian-lts-announce/2018/09/msg00010.html
- https://security.gentoo.org/glsa/201612-18
- http://openwall.com/lists/oss-security/2016/01/15/13
- http://www.securityfocus.com/bid/84427
- http://rhn.redhat.com/errata/RHSA-2016-0465.html
- http://rhn.redhat.com/errata/RHSA-2016-0741.html
- http://www.openssh.com/txt/release-7.2
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- https://anongit.mindrot.org/openssh.git/commit/?id=ed4ce82dbfa8a3a3c8ea6fa0db113c71e234416c
- https://bugzilla.redhat.com/show_bug.cgi?id=1298741
