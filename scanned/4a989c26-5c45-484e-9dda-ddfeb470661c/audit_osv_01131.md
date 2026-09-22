# [H] ALPINE-CVE-2018-20406

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-20406
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-20406
Type: osv

## Affected
- Alpine:v3.6: `python3` — affected >=0 <3.6.8-r0
- Alpine:v3.7: `python3` — affected >=0 <3.6.8-r0
- Alpine:v3.8: `python3` — affected >=0 <3.6.8-r0

## Details
Modules/_pickle.c in Python before 3.7.1 has an integer overflow via a large LONG_BINPUT value that is mishandled during a "resize to twice the size" attempt. This issue might cause memory exhaustion, but is only relevant if the pickle format is used for serializing tens or hundreds of gigabytes of data. This issue is fixed in: v3.4.10, v3.4.10rc1; v3.5.10, v3.5.10rc1, v3.5.7, v3.5.7rc1, v3.5.8, v3.5.8rc1, v3.5.8rc2, v3.5.9; v3.6.10, v3.6.10rc1, v3.6.11, v3.6.11rc1, v3.6.12, v3.6.7, v3.6.7rc1, v3.6.7rc2, v3.6.8, v3.6.8rc1, v3.6.9, v3.6.9rc1; v3.7.1, v3.7.1rc1, v3.7.1rc2, v3.7.2, v3.7.2rc1, v3.7.3, v3.7.3rc1, v3.7.4, v3.7.4rc1, v3.7.4rc2, v3.7.5, v3.7.5rc1, v3.7.6, v3.7.6rc1, v3.7.7, v3.7.7rc1, v3.7.8, v3.7.8rc1, v3.7.9.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-20406
