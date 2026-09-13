# [H] ALPINE-CVE-2024-25062

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-25062
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-25062
Type: osv

## Affected
- Alpine:v3.18: `libxml2` — affected >=2.12.0 <2.11.7-r0
- Alpine:v3.19: `libxml2` — affected >=2.12.0 <2.11.7-r0
- Alpine:v3.20: `libxml2` — affected >=2.12.0 <2.12.5-r0
- Alpine:v3.21: `libxml2` — affected >=2.12.0 <2.12.5-r0
- Alpine:v3.22: `libxml2` — affected >=2.12.0 <2.12.5-r0
- Alpine:v3.23: `libxml2` — affected >=2.12.0 <2.12.5-r0
- Alpine:v3.24: `libxml2` — affected >=2.12.0 <2.12.5-r0

## Details
An issue was discovered in libxml2 before 2.11.7 and 2.12.x before 2.12.5. When using the XML Reader interface with DTD validation and XInclude expansion enabled, processing crafted XML documents can lead to an xmlValidatePopElement use-after-free.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-25062
