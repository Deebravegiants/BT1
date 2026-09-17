# [H] CVE-2019-3833

## Summary
Severity: High
Advisory: CVE-2019-3833
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-14
Source: https://osv.dev/vulnerability/CVE-2019-3833
Type: osv

## Details
Openwsman, versions up to and including 2.6.9, are vulnerable to infinite loop in process_connection() when parsing specially crafted HTTP requests. A remote, unauthenticated attacker can exploit this vulnerability by sending malicious HTTP request to cause denial of service to openwsman server.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2V5HJ355RSKMFQ7GRJAHRZNDVXASF7TA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B2HEZ7D7GF3HDF36JLGYXIK5URR66DS4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CXQP7UDPRZIZ4LM7FEJCTC2EDUYVOR2J/
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00065.html
- http://www.securityfocus.com/bid/107367
- http://bugzilla.suse.com/show_bug.cgi?id=1122623
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3833
