# [C] ALPINE-CVE-2024-47175

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-47175
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-47175
Type: osv

## Affected
- Alpine:v3.19: `cups` — affected >=0 <2.4.9-r1
- Alpine:v3.20: `cups` — affected >=0 <2.4.9-r1
- Alpine:v3.21: `cups` — affected >=0 <2.4.10-r1
- Alpine:v3.22: `cups` — affected >=0 <2.4.10-r1
- Alpine:v3.23: `cups` — affected >=0 <2.4.10-r1
- Alpine:v3.24: `cups` — affected >=0 <2.4.10-r1

## Details
CUPS is a standards-based, open-source printing system, and `libppd` can be used for legacy PPD file support. The `libppd` function `ppdCreatePPDFromIPP2` does not sanitize IPP attributes when creating the PPD buffer. When used in combination with other functions such as `cfGetPrinterAttributes5`, can result in user controlled input and ultimately code execution via Foomatic. This vulnerability can be part of an exploit chain leading to remote code execution (RCE), as described in CVE-2024-47176.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-47175
