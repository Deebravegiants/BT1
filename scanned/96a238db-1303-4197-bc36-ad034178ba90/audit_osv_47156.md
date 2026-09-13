# [H] CVE-2016-0741

## Summary
Severity: High
Advisory: CVE-2016-0741
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-19
Source: https://osv.dev/vulnerability/CVE-2016-0741
Type: osv

## Details
slapd/connection.c in 389 Directory Server (formerly Fedora Directory Server) 1.3.4.x before 1.3.4.7 allows remote attackers to cause a denial of service (infinite loop and connection blocking) by leveraging an abnormally closed connection.

## References
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/bid/82343
- https://fedorahosted.org/389/changeset/cd45d032421b0ecf76d8cbb9b1c3aeef7680d9a2/
- https://fedorahosted.org/389/ticket/48412
- http://rhn.redhat.com/errata/RHSA-2016-0204.html
- http://directory.fedoraproject.org/docs/389ds/releases/release-1-3-4-7.html
