# [C] CVE-2016-2074

## Summary
Severity: Critical
Advisory: CVE-2016-2074
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-07-03
Source: https://osv.dev/vulnerability/CVE-2016-2074
Type: osv

## Details
Buffer overflow in lib/flow.c in ovs-vswitchd in Open vSwitch 2.2.x and 2.3.x before 2.3.3 and 2.4.x before 2.4.1 allows remote attackers to execute arbitrary code via crafted MPLS packets, as demonstrated by a long string in an ovs-appctl command.

## References
- http://www.securityfocus.com/bid/85700
- https://security-tracker.debian.org/tracker/CVE-2016-2074
- https://support.citrix.com/article/CTX232655
- http://openvswitch.org/pipermail/announce/2016-March/000082.html
- http://rhn.redhat.com/errata/RHSA-2016-0523.html
- http://rhn.redhat.com/errata/RHSA-2016-0524.html
- http://rhn.redhat.com/errata/RHSA-2016-0537.html
- http://www.debian.org/security/2016/dsa-3533
- https://access.redhat.com/errata/RHSA-2016:0615
- https://security.gentoo.org/glsa/201701-07
- https://bugzilla.redhat.com/show_bug.cgi?id=1318553
- http://openvswitch.org/pipermail/announce/2016-March/000083.html
