# [H] ALPINE-CVE-2021-41158

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-41158
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-10-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41158
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
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.10.7, an attacker can perform a SIP digest leak attack against FreeSWITCH and receive the challenge response of a gateway configured on the FreeSWITCH server. This is done by challenging FreeSWITCH's SIP requests with the realm set to that of the gateway, thus forcing FreeSWITCH to respond with the challenge response which is based on the password of that targeted gateway. Abuse of this vulnerability allows attackers to potentially recover gateway passwords by performing a fast offline password cracking attack on the challenge response. The attacker does not require special network privileges, such as the ability to sniff the FreeSWITCH's network traffic, to exploit this issue. Instead, what is required for this attack to work is the ability to cause the victim server to send SIP request messages to the malicious party. Additionally, to exploit this issue, the attacker needs to specify the correct realm which might in some cases be considered secret. However, because many gateways are actually public, this information can easily be retrieved. The vulnerability appears to be due to the code which handles challenges in `sofia_reg.c`, `sofia_reg_handle_sip_r_challenge()` which does not check if the challenge is originating from the actual gateway. The lack of these checks allows arbitrary UACs (and gateways) to challenge any request sent by FreeSWITCH with the realm of the gateway being targeted. This issue is patched in version 10.10.7. Maintainers recommend that one should create an association between a SIP session for each gateway and its realm to make a check be put into place for this association when responding to challenges.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41158
