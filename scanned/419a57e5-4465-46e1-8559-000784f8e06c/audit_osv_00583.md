# [H] ALPINE-CVE-2017-17405

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-17405
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17405
Type: osv

## Affected
- Alpine:v3.10: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.11: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.12: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.13: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.14: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.15: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.16: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.17: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.18: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.19: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.20: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.21: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.22: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.23: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.24: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.3: `ruby` — affected >=2.2 <2.2.9-r0
- Alpine:v3.4: `ruby` — affected >=2.2 <2.3.6-r0
- Alpine:v3.5: `ruby` — affected >=2.2 <2.3.6-r0
- Alpine:v3.6: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.7: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.8: `ruby` — affected >=2.2 <2.4.3-r0
- Alpine:v3.9: `ruby` — affected >=2.2 <2.4.3-r0

## Details
Ruby before 2.4.3 allows Net::FTP command injection. Net::FTP#get, getbinaryfile, gettextfile, put, putbinaryfile, and puttextfile use Kernel#open to open a local file. If the localfile argument starts with the "|" pipe character, the command following the pipe character is executed. The default value of localfile is File.basename(remotefile), so malicious FTP servers could cause arbitrary command execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17405
