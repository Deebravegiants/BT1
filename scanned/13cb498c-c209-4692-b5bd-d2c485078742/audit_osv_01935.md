# [M] ALPINE-CVE-2020-28327

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-28327
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-28327
Type: osv

## Affected
- Alpine:v3.12: `asterisk` — affected >=13.0.0 <16.14.1-r0
- Alpine:v3.13: `asterisk` — affected >=13.0.0 <18.0.1-r0
- Alpine:v3.14: `asterisk` — affected >=13.0.0 <18.0.1-r0
- Alpine:v3.15: `asterisk` — affected >=13.0.0 <18.0.1-r0
- Alpine:v3.16: `asterisk` — affected >=13.0.0 <18.0.1-r0
- Alpine:v3.17: `asterisk` — affected >=13.0.0 <18.0.1-r0
- Alpine:v3.18: `asterisk` — affected >=13.0.0 <18.0.1-r0
- Alpine:v3.19: `asterisk` — affected >=13.0.0 <18.0.1-r0
- Alpine:v3.20: `asterisk` — affected >=13.0.0 <18.0.1-r0
- Alpine:v3.21: `asterisk` — affected >=13.0.0 <18.0.1-r0
- Alpine:v3.22: `asterisk` — affected >=13.0.0 <18.0.1-r0
- Alpine:v3.23: `asterisk` — affected >=13.0.0 <18.0.1-r0
- Alpine:v3.24: `asterisk` — affected >=13.0.0 <18.0.1-r0

## Details
A res_pjsip_session crash was discovered in Asterisk Open Source 13.x before 13.37.1, 16.x before 16.14.1, 17.x before 17.8.1, and 18.x before 18.0.1. and Certified Asterisk before 16.8-cert5. Upon receiving a new SIP Invite, Asterisk did not return the created dialog locked or referenced. This caused a gap between the creation of the dialog object, and its next use by the thread that created it. Depending on some off-nominal circumstances and timing, it was possible for another thread to free said dialog in this gap. Asterisk could then crash when the dialog object, or any of its dependent objects, were dereferenced or accessed next by the initial-creation thread. Note, however, that this crash can only occur when using a connection-oriented protocol (e.g., TCP or TLS, but not UDP) for SIP transport. Also, the remote client must be authenticated, or Asterisk must be configured for anonymous calling.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-28327
