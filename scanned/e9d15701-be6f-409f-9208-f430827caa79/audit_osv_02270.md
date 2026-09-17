# [H] ALPINE-CVE-2021-37624

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-37624
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-37624
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
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. Prior to version 1.10.7, FreeSWITCH does not authenticate SIP MESSAGE requests, leading to spam and message spoofing. By default, SIP requests of the type MESSAGE (RFC 3428) are not authenticated in the affected versions of FreeSWITCH. MESSAGE requests are relayed to SIP user agents registered with the FreeSWITCH server without requiring any authentication. Although this behaviour can be changed by setting the `auth-messages` parameter to `true`, it is not the default setting. Abuse of this security issue allows attackers to send SIP MESSAGE messages to any SIP user agent that is registered with the server without requiring authentication. Additionally, since no authentication is required, chat messages can be spoofed to appear to come from trusted entities. Therefore, abuse can lead to spam and enable social engineering, phishing and similar attacks. This issue is patched in version 1.10.7. Maintainers recommend that this SIP message type is authenticated by default so that FreeSWITCH administrators do not need to be explicitly set the `auth-messages` parameter. When following such a recommendation, a new parameter can be introduced to explicitly disable authentication.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-37624
