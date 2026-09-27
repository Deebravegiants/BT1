# [C] ALPINE-CVE-2023-22741

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-22741
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-22741
Type: osv

## Affected
- Alpine:v3.14: `sofia-sip` — affected >=0 <1.13.11-r0
- Alpine:v3.15: `sofia-sip` — affected >=0 <1.13.11-r0
- Alpine:v3.16: `sofia-sip` — affected >=0 <1.13.11-r0
- Alpine:v3.17: `sofia-sip` — affected >=0 <1.13.11-r0
- Alpine:v3.18: `sofia-sip` — affected >=0 <1.13.11-r0
- Alpine:v3.19: `sofia-sip` — affected >=0 <1.13.11-r0
- Alpine:v3.20: `sofia-sip` — affected >=0 <1.13.11-r0
- Alpine:v3.21: `sofia-sip` — affected >=0 <1.13.11-r0
- Alpine:v3.22: `sofia-sip` — affected >=0 <1.13.11-r0
- Alpine:v3.23: `sofia-sip` — affected >=0 <1.13.11-r0
- Alpine:v3.24: `sofia-sip` — affected >=0 <1.13.11-r0

## Details
Sofia-SIP is an open-source SIP User-Agent library, compliant with the IETF RFC3261 specification. In affected versions Sofia-SIP **lacks both message length and attributes length checks** when it handles STUN packets, leading to controllable heap-over-flow. For example, in stun_parse_attribute(), after we get the attribute's type and length value, the length will be used directly to copy from the heap, regardless of the message's left size. Since network users control the overflowed length, and the data is written to heap chunks later, attackers may achieve remote code execution by heap grooming or other exploitation methods. The bug was introduced 16 years ago in sofia-sip 1.12.4 (plus some patches through 12/21/2006) to in tree libs with git-svn-id: http://svn.freeswitch.org/svn/freeswitch/trunk@3774 d0543943-73ff-0310-b7d9-9358b9ac24b2. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-22741
