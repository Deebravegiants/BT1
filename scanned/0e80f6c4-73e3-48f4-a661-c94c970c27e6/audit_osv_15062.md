# [M] CVE-2019-13161

## Summary
Severity: Medium
Advisory: CVE-2019-13161
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-12
Source: https://osv.dev/vulnerability/CVE-2019-13161
Type: osv

## Details
An issue was discovered in Asterisk Open Source through 13.27.0, 14.x and 15.x through 15.7.2, and 16.x through 16.4.0, and Certified Asterisk through 13.21-cert3. A pointer dereference in chan_sip while handling SDP negotiation allows an attacker to crash Asterisk when handling an SDP answer to an outgoing T.38 re-invite. To exploit this vulnerability an attacker must cause the chan_sip module to send a T.38 re-invite request to them. Upon receipt, the attacker must send an SDP answer containing both a T.38 UDPTL stream and another media stream containing only a codec (which is not permitted according to the chan_sip configuration).

## References
- http://downloads.digium.com/pub/security/AST-2019-003.html
- https://lists.debian.org/debian-lts-announce/2019/11/msg00038.html
- https://lists.debian.org/debian-lts-announce/2022/04/msg00001.html
- https://issues.asterisk.org/jira/browse/ASTERISK-28465
