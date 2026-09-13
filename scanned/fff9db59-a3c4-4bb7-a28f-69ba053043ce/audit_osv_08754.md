# [M] CVE-2016-5696

## Summary
Severity: Medium
Advisory: CVE-2016-5696
CVSS: 4.8 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-5696
Type: osv

## Details
net/ipv4/tcp_input.c in the Linux kernel before 4.7 does not properly determine the rate of challenge ACK segments, which makes it easier for remote attackers to hijack TCP sessions via a blind in-window attack.

## References
- https://security.paloaltonetworks.com/CVE-2016-5696
- https://kc.mcafee.com/corporate/index?page=content&id=SB10167
- http://www.securitytracker.com/id/1036625
- http://www.securityfocus.com/bid/91704
- http://www.openwall.com/lists/oss-security/2016/07/12/2
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.ubuntu.com/usn/USN-3070-4
- http://rhn.redhat.com/errata/RHSA-2016-1633.html
- http://rhn.redhat.com/errata/RHSA-2016-1664.html
- http://www.ubuntu.com/usn/USN-3071-2
- http://rhn.redhat.com/errata/RHSA-2016-1631.html
- http://www.ubuntu.com/usn/USN-3070-2
- http://www.ubuntu.com/usn/USN-3071-1
- http://rhn.redhat.com/errata/RHSA-2016-1632.html
- http://rhn.redhat.com/errata/RHSA-2016-1657.html
- http://www.ubuntu.com/usn/USN-3070-3
- http://www.ubuntu.com/usn/USN-3072-2
- https://www.arista.com/en/support/advisories-notices/security-advisories/1461-security-advisory-23
- http://www.ubuntu.com/usn/USN-3072-1
- http://www.ubuntu.com/usn/USN-3070-1
