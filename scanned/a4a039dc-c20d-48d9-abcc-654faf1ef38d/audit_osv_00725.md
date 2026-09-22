# [H] ALPINE-CVE-2017-7468

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7468
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7468
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.11: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.12: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.13: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.14: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.15: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.16: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.2: `curl` — affected >=0 <7.52.1-r1
- Alpine:v3.20: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.3: `curl` — affected >=0 <7.52.1-r1
- Alpine:v3.4: `curl` — affected >=0 <7.52.1-r2
- Alpine:v3.5: `curl` — affected >=0 <7.52.1-r3
- Alpine:v3.6: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.7: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.8: `curl` — affected >=0 <7.54.0-r0
- Alpine:v3.9: `curl` — affected >=0 <7.54.0-r0

## Details
In curl and libcurl 7.52.0 to and including 7.53.1, libcurl would attempt to resume a TLS session even if the client certificate had changed. That is unacceptable since a server by specification is allowed to skip the client certificate check on resume, and may instead use the old identity which was established by the previous certificate (or no certificate). libcurl supports by default the use of TLS session id/ticket to resume previous TLS sessions to speed up subsequent TLS handshakes. They are used when for any reason an existing TLS connection couldn't be kept alive to make the next handshake faster. This flaw is a regression and identical to CVE-2016-5419 reported on August 3rd 2016, but affecting a different version range.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7468
