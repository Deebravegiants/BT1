# [H] CVE-2019-3816

## Summary
Severity: High
Advisory: CVE-2019-3816
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-03-14
Source: https://osv.dev/vulnerability/CVE-2019-3816
Type: osv

## Details
Openwsman, versions up to and including 2.6.9, are vulnerable to arbitrary file disclosure because the working directory of openwsmand daemon was set to root directory. A remote, unauthenticated attacker can exploit this vulnerability by sending a specially crafted HTTP request to openwsman server.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2V5HJ355RSKMFQ7GRJAHRZNDVXASF7TA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B2HEZ7D7GF3HDF36JLGYXIK5URR66DS4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CXQP7UDPRZIZ4LM7FEJCTC2EDUYVOR2J/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00065.html
- http://www.securityfocus.com/bid/107368
- http://www.securityfocus.com/bid/107409
- https://access.redhat.com/errata/RHSA-2019:0638
- https://access.redhat.com/errata/RHSA-2019:0972
- http://bugzilla.suse.com/show_bug.cgi?id=1122623
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3816
