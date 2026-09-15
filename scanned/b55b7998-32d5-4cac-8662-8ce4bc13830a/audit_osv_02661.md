# [M] ALPINE-CVE-2022-4203

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-4203
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-4203
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.0.8-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.8-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.8-r0

## Details
A read buffer overrun can be triggered in X.509 certificate verification,
specifically in name constraint checking. Note that this occurs
after certificate chain signature verification and requires either a
CA to have signed the malicious certificate or for the application to
continue certificate verification despite failure to construct a path
to a trusted issuer.

The read buffer overrun might result in a crash which could lead to
a denial of service attack. In theory it could also result in the disclosure
of private memory contents (such as private keys, or sensitive plaintext)
although we are not aware of any working exploit leading to memory
contents disclosure as of the time of release of this advisory.

In a TLS client, this can be triggered by connecting to a malicious
server. In a TLS server, this can be triggered if the server requests
client authentication and a malicious client connects.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-4203
