# [M] ALPINE-CVE-2023-49786

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-49786
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-49786
Type: osv

## Affected
- Alpine:v3.16: `asterisk` — affected >=19.0.0 <18.20.2-r0
- Alpine:v3.17: `asterisk` — affected >=19.0.0 <18.20.2-r0
- Alpine:v3.18: `asterisk` — affected >=19.0.0 <18.20.2-r0
- Alpine:v3.19: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.20: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.21: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.22: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.23: `asterisk` — affected >=19.0.0 <20.5.1-r0
- Alpine:v3.24: `asterisk` — affected >=19.0.0 <20.5.1-r0

## Details
Asterisk is an open source private branch exchange and telephony toolkit. In Asterisk prior to versions 18.20.1, 20.5.1, and 21.0.1; as well as certified-asterisk prior to 18.9-cert6; Asterisk is susceptible to a DoS due to a race condition in the hello handshake phase of the DTLS protocol when handling DTLS-SRTP for media setup. This attack can be done continuously, thus denying new DTLS-SRTP encrypted calls during the attack. Abuse of this vulnerability may lead to a massive Denial of Service on vulnerable Asterisk servers for calls that rely on DTLS-SRTP. Commit d7d7764cb07c8a1872804321302ef93bf62cba05 contains a fix, which is part of versions 18.20.1, 20.5.1, 21.0.1, amd 18.9-cert6.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-49786
