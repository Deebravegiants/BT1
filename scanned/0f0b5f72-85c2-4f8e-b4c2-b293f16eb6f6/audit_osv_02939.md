# [M] ALPINE-CVE-2023-51443

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-51443
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-51443
Type: osv

## Affected
- Alpine:v3.17: `freeswitch` — affected >=0 <1.10.11-r0
- Alpine:v3.18: `freeswitch` — affected >=0 <1.10.11-r0
- Alpine:v3.19: `freeswitch` — affected >=0 <1.10.11-r0
- Alpine:v3.20: `freeswitch` — affected >=0 <1.10.11-r0
- Alpine:v3.21: `freeswitch` — affected >=0 <1.10.11-r0
- Alpine:v3.22: `freeswitch` — affected >=0 <1.10.11-r0
- Alpine:v3.23: `freeswitch` — affected >=0 <1.10.11-r0
- Alpine:v3.24: `freeswitch` — affected >=0 <1.10.11-r0

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.10.11, when handling DTLS-SRTP for media setup, FreeSWITCH is susceptible to Denial of Service due to a race condition in the hello handshake phase of the DTLS protocol. This attack can be done continuously, thus denying new DTLS-SRTP encrypted calls during the attack. If an attacker manages to send a ClientHello DTLS message with an invalid CipherSuite (such as `TLS_NULL_WITH_NULL_NULL`) to the port on the FreeSWITCH server that is expecting packets from the caller, a DTLS error is generated. This results in the media session being torn down, which is followed by teardown at signaling (SIP) level too. Abuse of this vulnerability may lead to a massive Denial of Service on vulnerable FreeSWITCH servers for calls that rely on DTLS-SRTP. To address this vulnerability, upgrade FreeSWITCH to 1.10.11 which includes the security fix. The solution implemented is to drop all packets from addresses that have not been validated by an ICE check.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-51443
