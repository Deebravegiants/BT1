# [H] ALPINE-CVE-2022-43551

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-43551
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-12-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-43551
Type: osv

## Affected
- Alpine:v3.14: `curl` — affected >=7.77.0 <7.79.1-r4
- Alpine:v3.15: `curl` — affected >=7.77.0 <7.80.0-r5
- Alpine:v3.16: `curl` — affected >=7.77.0 <7.83.1-r5
- Alpine:v3.17: `curl` — affected >=7.77.0 <7.87.0-r0
- Alpine:v3.18: `curl` — affected >=7.77.0 <7.87.0-r0
- Alpine:v3.19: `curl` — affected >=7.77.0 <7.87.0-r0
- Alpine:v3.20: `curl` — affected >=7.77.0 <7.87.0-r0
- Alpine:v3.21: `curl` — affected >=7.77.0 <7.87.0-r0
- Alpine:v3.22: `curl` — affected >=7.77.0 <7.87.0-r0
- Alpine:v3.23: `curl` — affected >=7.77.0 <7.87.0-r0
- Alpine:v3.24: `curl` — affected >=7.77.0 <7.87.0-r0

## Details
A vulnerability exists in curl <7.87.0 HSTS check that could be bypassed to trick it to keep using HTTP. Using its HSTS support, curl can be instructed to use HTTPS instead of using an insecure clear-text HTTP step even when HTTP is provided in the URL. However, the HSTS mechanism could be bypassed if the host name in the given URL first uses IDN characters that get replaced to ASCII counterparts as part of the IDN conversion. Like using the character UTF-8 U+3002 (IDEOGRAPHIC FULL STOP) instead of the common ASCII full stop (U+002E) `.`. Then in a subsequent request, it does not detect the HSTS state and makes a clear text transfer. Because it would store the info IDN encoded but look for it IDN decoded.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-43551
