# [M] ALPINE-CVE-2022-30115

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-30115
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-30115
Type: osv

## Affected
- Alpine:v3.16: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.17: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.18: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.19: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.20: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.21: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.22: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.23: `curl` — affected >=7.82.0 <7.83.1-r0
- Alpine:v3.24: `curl` — affected >=7.82.0 <7.83.1-r0

## Details
Using its HSTS support, curl can be instructed to use HTTPS directly insteadof using an insecure clear-text HTTP step even when HTTP is provided in theURL. This mechanism could be bypassed if the host name in the given URL used atrailing dot while not using one when it built the HSTS cache. Or the otherway around - by having the trailing dot in the HSTS cache and *not* using thetrailing dot in the URL.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-30115
