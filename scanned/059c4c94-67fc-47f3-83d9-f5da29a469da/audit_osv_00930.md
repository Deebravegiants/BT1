# [C] ALPINE-CVE-2018-11652

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-11652
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-11652
Type: osv

## Affected
- Alpine:v3.11: `nikto` — affected >=0 <2.1.6-r2
- Alpine:v3.12: `nikto` — affected >=0 <2.1.6-r2
- Alpine:v3.13: `nikto` — affected >=0 <2.1.6-r2
- Alpine:v3.14: `nikto` — affected >=0 <2.1.6-r2
- Alpine:v3.15: `nikto` — affected >=0 <2.1.6-r2
- Alpine:v3.16: `nikto` — affected >=0 <2.1.6-r2
- Alpine:v3.17: `nikto` — affected >=0 <2.1.6-r2
- Alpine:v3.18: `nikto` — affected >=0 <2.1.6-r2

## Details
CSV Injection vulnerability in Nikto 2.1.6 and earlier allows remote attackers to inject arbitrary OS commands via the Server field in an HTTP response header, which is directly injected into a CSV report.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-11652
