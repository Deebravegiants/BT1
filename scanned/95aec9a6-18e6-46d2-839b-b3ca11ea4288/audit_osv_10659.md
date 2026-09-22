# [C] CVE-2017-18017

## Summary
Severity: Critical
Advisory: CVE-2017-18017
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-03
Source: https://osv.dev/vulnerability/CVE-2017-18017
Type: osv

## Details
The tcpmss_mangle_packet function in net/netfilter/xt_TCPMSS.c in the Linux kernel before 4.11, and 4.9.x before 4.9.36, allows remote attackers to cause a denial of service (use-after-free and memory corruption) or possibly have unspecified other impact by leveraging the presence of xt_TCPMSS in an iptables action.

## References
- http://lists.opensuse.org/opensuse-security-announce/2018-02/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2018-03/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2018-04/msg00014.html
- https://support.f5.com/csp/article/K18352029
- http://lists.opensuse.org/opensuse-security-announce/2018-02/msg00047.html
- http://www.securityfocus.com/bid/102367
- https://access.redhat.com/errata/RHSA-2018:1170
- http://lists.opensuse.org/opensuse-security-announce/2018-02/msg00013.html
- http://lists.opensuse.org/opensuse-security-announce/2018-03/msg00067.html
- http://www.ubuntu.com/usn/USN-3583-1
- https://lkml.org/lkml/2017/4/2/13
- https://usn.ubuntu.com/3583-1/
- https://www.debian.org/security/2018/dsa-4187
- http://lists.opensuse.org/opensuse-security-announce/2018-02/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2018-03/msg00070.html
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1319
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2018-02/msg00015.html
- http://www.ubuntu.com/usn/USN-3583-2
