# [C] ALPINE-CVE-2021-22945

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-22945
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-09-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22945
Type: osv

## Affected
- Alpine:v3.11: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.12: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.13: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.14: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.15: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.16: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.79.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.79.0-r0

## Details
When sending data to an MQTT server, libcurl <= 7.73.0 and 7.78.0 could in some circumstances erroneously keep a pointer to an already freed memory area and both use that again in a subsequent call to send data and also free it *again*.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22945
