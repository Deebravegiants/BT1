# [H] ALPINE-CVE-2021-41145

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-41145
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-41145
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
FreeSWITCH is a Software Defined Telecom Stack enabling the digital transformation from proprietary telecom switches to a software implementation that runs on any commodity hardware. FreeSWITCH prior to version 1.10.7 is susceptible to Denial of Service via SIP flooding. When flooding FreeSWITCH with SIP messages, it was observed that after a number of seconds the process was killed by the operating system due to memory exhaustion. By abusing this vulnerability, an attacker is able to crash any FreeSWITCH instance by flooding it with SIP messages, leading to Denial of Service. The attack does not require authentication and can be carried out over UDP, TCP or TLS. This issue was patched in version 1.10.7.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-41145
