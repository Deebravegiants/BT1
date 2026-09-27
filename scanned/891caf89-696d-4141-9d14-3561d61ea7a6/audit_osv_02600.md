# [C] ALPINE-CVE-2022-3515

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-3515
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-3515
Type: osv

## Affected
- Alpine:v3.14: `libksba` — affected >=0 <1.5.1-r1
- Alpine:v3.15: `libksba` — affected >=0 <1.6.3-r0
- Alpine:v3.16: `libksba` — affected >=0 <1.6.3-r0
- Alpine:v3.17: `libksba` — affected >=0 <1.6.2-r0
- Alpine:v3.18: `libksba` — affected >=0 <1.6.2-r0
- Alpine:v3.19: `libksba` — affected >=0 <1.6.2-r0
- Alpine:v3.20: `libksba` — affected >=0 <1.6.2-r0
- Alpine:v3.21: `libksba` — affected >=0 <1.6.2-r0
- Alpine:v3.22: `libksba` — affected >=0 <1.6.2-r0
- Alpine:v3.23: `libksba` — affected >=0 <1.6.2-r0
- Alpine:v3.24: `libksba` — affected >=0 <1.6.2-r0

## Details
A vulnerability was found in the Libksba library due to an integer overflow within the CRL parser. The vulnerability can be exploited remotely for code execution on the target system by passing specially crafted data to the application, for example, a malicious S/MIME attachment.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-3515
