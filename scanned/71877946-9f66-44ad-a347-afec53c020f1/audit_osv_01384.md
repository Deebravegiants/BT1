# [H] ALPINE-CVE-2019-12816

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12816
Ecosystem: Alpine:v3.7, Alpine:v3.8
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12816
Type: osv

## Affected
- Alpine:v3.7: `znc` — affected >=0 <1.7.1-r1
- Alpine:v3.8: `znc` — affected >=0 <1.7.1-r1

## Details
Modules.cpp in ZNC before 1.7.4-rc1 allows remote authenticated non-admin users to escalate privileges and execute arbitrary code by loading a module with a crafted name.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12816
