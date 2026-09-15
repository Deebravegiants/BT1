# [H] ALPINE-CVE-2022-1620

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-1620
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1620
Type: osv

## Affected
- Alpine:v3.16: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.17: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.18: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.19: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.20: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.21: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.22: `vim` — affected >=0 <8.2.4969-r0
- Alpine:v3.23: `vim` — affected >=0 <8.2.4969-r0

## Details
NULL Pointer Dereference in function vim_regexec_string at regexp.c:2729 in GitHub repository vim/vim prior to 8.2.4901. NULL Pointer Dereference in function vim_regexec_string at regexp.c:2729 allows attackers to cause a denial of service (application crash) via a crafted input.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1620
