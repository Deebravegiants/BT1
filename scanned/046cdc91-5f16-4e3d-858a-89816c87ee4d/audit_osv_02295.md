# [H] ALPINE-CVE-2021-41105

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-41105
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41105
Type: osv

## Affected
- Alpine:v3.15: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.16: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.17: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.18: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.19: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.20: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.21: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.22: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.23: `freeswitch` — affected >=0 <1.10.7-r0
- Alpine:v3.24: `freeswitch` — affected >=0 <1.10.7-r0

## Details
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. When handling SRTP calls, FreeSWITCH prior to version 1.10.7 is susceptible to a DoS where calls can be terminated by remote attackers. This attack can be done continuously, thus denying encrypted calls during the attack. When a media port that is handling SRTP traffic is flooded with a specially crafted SRTP packet, the call is terminated leading to denial of service. This issue was reproduced when using the SDES key exchange mechanism in a SIP environment as well as when using the DTLS key exchange mechanism in a WebRTC environment. The call disconnection occurs due to line 6331 in the source file `switch_rtp.c`, which disconnects the call when the total number of SRTP errors reach a hard-coded threshold (100). By abusing this vulnerability, an attacker is able to disconnect any ongoing calls that are using SRTP. The attack does not require authentication or any special foothold in the caller's or the callee's network. This issue is patched in version 1.10.7.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41105
