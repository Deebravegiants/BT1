# [M] CVE-2019-18790

## Summary
Severity: Medium
Advisory: CVE-2019-18790
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2019-11-22
Source: https://osv.dev/vulnerability/CVE-2019-18790
Type: osv

## Details
An issue was discovered in channels/chan_sip.c in Sangoma Asterisk 13.x before 13.29.2, 16.x before 16.6.2, and 17.x before 17.0.1, and Certified Asterisk 13.21 before cert5. A SIP request can be sent to Asterisk that can change a SIP peer's IP address. A REGISTER does not need to occur, and calls can be hijacked as a result. The only thing that needs to be known is the peer's name; authentication details such as passwords do not need to be known. This vulnerability is only exploitable when the nat option is set to the default, or auto_force_rport.

## References
- https://lists.debian.org/debian-lts-announce/2019/11/msg00038.html
- https://lists.debian.org/debian-lts-announce/2022/04/msg00001.html
- https://www.asterisk.org/downloads/security-advisories
- http://downloads.asterisk.org/pub/security/AST-2019-006.html
