# [C] ALPINE-CVE-2015-8367

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2015-8367
Ecosystem: Alpine:v3.3
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2015-8367
Type: osv

## Affected
- Alpine:v3.3: `libraw` — affected >=0 <0.17.1-r0

## Details
The phase_one_correct function in Libraw before 0.17.1 allows attackers to cause memory errors and possibly execute arbitrary code, related to memory object initialization.

## References
- https://security.alpinelinux.org/vuln/CVE-2015-8367
