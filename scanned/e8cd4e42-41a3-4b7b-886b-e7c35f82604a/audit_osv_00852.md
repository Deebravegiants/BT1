# [C] ALPINE-CVE-2018-0500

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-0500
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-0500
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.11: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.12: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.13: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.14: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.15: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.16: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.17: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.18: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.19: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.20: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.21: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.22: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.23: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.24: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.5: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.6: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.7: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.8: `curl` — affected >=7.54.1 <7.61.0-r0
- Alpine:v3.9: `curl` — affected >=7.54.1 <7.61.0-r0

## Details
Curl_smtp_escape_eob in lib/smtp.c in curl 7.54.1 to and including curl 7.60.0 has a heap-based buffer overflow that might be exploitable by an attacker who can control the data that curl transmits over SMTP with certain settings (i.e., use of a nonstandard --limit-rate argument or CURLOPT_BUFFERSIZE value).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-0500
