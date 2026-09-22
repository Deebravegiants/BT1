# [H] ALPINE-CVE-2022-3786

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-3786
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3786
Type: osv

## Affected
- Alpine:v3.17: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.7-r0
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.0.7-r0
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.0.7-r0
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.0.7-r0
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.0.7-r0
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.0.7-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.0.7-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.0.7-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.7-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.7-r0

## Details
A buffer overrun can be triggered in X.509 certificate verification, specifically in name constraint checking. Note that this occurs after certificate chain signature verification and requires either a CA to have signed a malicious certificate or for an application to continue certificate verification despite failure to construct a path to a trusted issuer. An attacker can craft a malicious email address in a certificate to overflow an arbitrary number of bytes containing the `.' character (decimal 46) on the stack. This buffer overflow could result in a crash (causing a denial of service). In a TLS client, this can be triggered by connecting to a malicious server. In a TLS server, this can be triggered if the server requests client authentication and a malicious client connects.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3786
