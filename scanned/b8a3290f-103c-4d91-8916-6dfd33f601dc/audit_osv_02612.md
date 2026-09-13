# [H] ALPINE-CVE-2022-3602

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-3602
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3602
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
A buffer overrun can be triggered in X.509 certificate verification, specifically in name constraint checking. Note that this occurs after certificate chain signature verification and requires either a CA to have signed the malicious certificate or for the application to continue certificate verification despite failure to construct a path to a trusted issuer. An attacker can craft a malicious email address to overflow four attacker-controlled bytes on the stack. This buffer overflow could result in a crash (causing a denial of service) or potentially remote code execution. Many platforms implement stack overflow protections which would mitigate against the risk of remote code execution. The risk may be further mitigated based on stack layout for any given platform/compiler. Pre-announcements of CVE-2022-3602 described this issue as CRITICAL. Further analysis based on some of the mitigating factors described above have led this to be downgraded to HIGH. Users are still encouraged to upgrade to a new version as soon as possible. In a TLS client, this can be triggered by connecting to a malicious server. In a TLS server, this can be triggered if the server requests client authentication and a malicious client connects. Fixed in OpenSSL 3.0.7 (Affected 3.0.0,3.0.1,3.0.2,3.0.3,3.0.4,3.0.5,3.0.6).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3602
