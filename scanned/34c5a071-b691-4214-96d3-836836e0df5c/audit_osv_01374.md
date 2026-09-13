# [C] ALPINE-CVE-2019-12519

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-12519
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12519
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=3.0 <4.11-r0
- Alpine:v3.11: `squid` — affected >=3.0 <4.11-r0
- Alpine:v3.9: `squid` — affected >=3.0 <4.11-r0

## Details
An issue was discovered in Squid through 4.7. When handling the tag esi:when when ESI is enabled, Squid calls ESIExpression::Evaluate. This function uses a fixed stack buffer to hold the expression while it's being evaluated. When processing the expression, it could either evaluate the top of the stack, or add a new member to the stack. When adding a new member, there is no check to ensure that the stack won't overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12519
