# [H] ALPINE-CVE-2020-15049

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-15049
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-15049
Type: osv

## Affected
- Alpine:v3.15: `squid` — affected >=2.0 <4.12.0-r0
- Alpine:v3.16: `squid` — affected >=2.0 <4.12.0-r0
- Alpine:v3.17: `squid` — affected >=2.0 <4.12.0-r0
- Alpine:v3.18: `squid` — affected >=2.0 <4.12.0-r0
- Alpine:v3.19: `squid` — affected >=2.0 <4.12.0-r0
- Alpine:v3.20: `squid` — affected >=2.0 <4.12.0-r0
- Alpine:v3.21: `squid` — affected >=2.0 <4.12.0-r0
- Alpine:v3.22: `squid` — affected >=2.0 <4.12.0-r0
- Alpine:v3.23: `squid` — affected >=2.0 <4.12.0-r0
- Alpine:v3.24: `squid` — affected >=2.0 <4.12.0-r0

## Details
An issue was discovered in http/ContentLengthInterpreter.cc in Squid before 4.12 and 5.x before 5.0.3. A Request Smuggling and Poisoning attack can succeed against the HTTP cache. The client sends an HTTP request with a Content-Length header containing "+\ "-" or an uncommon shell whitespace character prefix to the length field-value.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-15049
