# [H] ALPINE-CVE-2023-3341

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-3341
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-3341
Type: osv

## Affected
- Alpine:v3.15: `bind` — affected >=9.2.0 <9.16.44-r0
- Alpine:v3.16: `bind` — affected >=9.2.0 <9.16.44-r0
- Alpine:v3.17: `bind` — affected >=9.2.0 <9.18.19-r0
- Alpine:v3.18: `bind` — affected >=9.2.0 <9.18.19-r0
- Alpine:v3.19: `bind` — affected >=9.2.0 <9.18.19-r0
- Alpine:v3.20: `bind` — affected >=9.2.0 <9.18.19-r0
- Alpine:v3.21: `bind` — affected >=9.2.0 <9.18.19-r0
- Alpine:v3.22: `bind` — affected >=9.2.0 <9.18.19-r0
- Alpine:v3.23: `bind` — affected >=9.2.0 <9.18.19-r0
- Alpine:v3.24: `bind` — affected >=9.2.0 <9.18.19-r0

## Details
The code that processes control channel messages sent to `named` calls certain functions recursively during packet parsing. Recursion depth is only limited by the maximum accepted packet size; depending on the environment, this may cause the packet-parsing code to run out of available stack memory, causing `named` to terminate unexpectedly. Since each incoming control channel message is fully parsed before its contents are authenticated, exploiting this flaw does not require the attacker to hold a valid RNDC key; only network access to the control channel's configured TCP port is necessary.
This issue affects BIND 9 versions 9.2.0 through 9.16.43, 9.18.0 through 9.18.18, 9.19.0 through 9.19.16, 9.9.3-S1 through 9.16.43-S1, and 9.18.0-S1 through 9.18.18-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-3341
