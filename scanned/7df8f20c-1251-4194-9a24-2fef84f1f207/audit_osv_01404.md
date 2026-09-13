# [M] ALPINE-CVE-2019-13161

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-13161
Ecosystem: Alpine:v3.10, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13161
Type: osv

## Affected
- Alpine:v3.10: `asterisk` — affected >=13.0.0 <16.3.0-r2
- Alpine:v3.7: `asterisk` — affected >=13.0.0 <15.6.2-r0
- Alpine:v3.8: `asterisk` — affected >=13.0.0 <15.6.2-r0
- Alpine:v3.9: `asterisk` — affected >=13.0.0 <15.7.4-r0

## Details
An issue was discovered in Asterisk Open Source through 13.27.0, 14.x and 15.x through 15.7.2, and 16.x through 16.4.0, and Certified Asterisk through 13.21-cert3. A pointer dereference in chan_sip while handling SDP negotiation allows an attacker to crash Asterisk when handling an SDP answer to an outgoing T.38 re-invite. To exploit this vulnerability an attacker must cause the chan_sip module to send a T.38 re-invite request to them. Upon receipt, the attacker must send an SDP answer containing both a T.38 UDPTL stream and another media stream containing only a codec (which is not permitted according to the chan_sip configuration).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13161
