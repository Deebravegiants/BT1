# [H] ALPINE-CVE-2024-1931

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-1931
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-1931
Type: osv

## Affected
- Alpine:v3.17: `unbound` — affected >=1.18.0 <1.19.2-r0
- Alpine:v3.18: `unbound` — affected >=1.18.0 <1.19.2-r0
- Alpine:v3.19: `unbound` — affected >=1.18.0 <1.19.2-r0
- Alpine:v3.20: `unbound` — affected >=1.18.0 <1.19.2-r0
- Alpine:v3.21: `unbound` — affected >=1.18.0 <1.19.2-r0
- Alpine:v3.22: `unbound` — affected >=1.18.0 <1.19.2-r0
- Alpine:v3.23: `unbound` — affected >=1.18.0 <1.19.2-r0
- Alpine:v3.24: `unbound` — affected >=1.18.0 <1.19.2-r0

## Details
NLnet Labs Unbound version 1.18.0 up to and including version 1.19.1 contain a vulnerability that can cause denial of service by a certain code path that can lead to an infinite loop. Unbound 1.18.0 introduced a feature that removes EDE records from responses with size higher than the client's advertised buffer size. Before removing all the EDE records however, it would try to see if trimming the extra text fields on those records would result in an acceptable size while still retaining the EDE codes. Due to an unchecked condition, the code that trims the text of the EDE records could loop indefinitely. This happens when Unbound would reply with attached EDE information on a positive reply and the client's buffer size is smaller than the needed space to include EDE records. The vulnerability can only be triggered when the 'ede: yes' option is used; non default configuration. From version 1.19.2 on, the code is fixed to avoid looping indefinitely.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-1931
