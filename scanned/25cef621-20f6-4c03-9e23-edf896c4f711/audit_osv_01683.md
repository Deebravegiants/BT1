# [H] ALPINE-CVE-2019-9755

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-9755
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9755
Type: osv

## Affected
- Alpine:v3.10: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.11: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.12: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.13: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.14: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.15: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.16: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.17: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.18: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.19: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.20: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.21: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.22: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.23: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.24: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.8: `ntfs-3g` — affected >=0 <2017.3.23-r2
- Alpine:v3.9: `ntfs-3g` — affected >=0 <2017.3.23-r2

## Details
An integer underflow issue exists in ntfs-3g 2017.3.23. A local attacker could potentially exploit this by running /bin/ntfs-3g with specially crafted arguments from a specially crafted directory to cause a heap buffer overflow, resulting in a crash or the ability to execute arbitrary code. In installations where /bin/ntfs-3g is a setuid-root binary, this could lead to a local escalation of privileges.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9755
