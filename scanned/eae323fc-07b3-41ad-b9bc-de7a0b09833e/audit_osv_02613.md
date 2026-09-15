# [C] ALPINE-CVE-2022-36227

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-36227
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-36227
Type: osv

## Affected
- Alpine:v3.14: `libarchive` — affected >=3.0.0 <3.5.3-r1
- Alpine:v3.15: `libarchive` — affected >=3.0.0 <3.6.1-r1
- Alpine:v3.16: `libarchive` — affected >=3.0.0 <3.6.1-r1
- Alpine:v3.17: `libarchive` — affected >=3.0.0 <3.6.1-r2
- Alpine:v3.18: `libarchive` — affected >=3.0.0 <3.6.1-r2
- Alpine:v3.19: `libarchive` — affected >=3.0.0 <3.6.1-r2
- Alpine:v3.20: `libarchive` — affected >=3.0.0 <3.6.1-r2
- Alpine:v3.21: `libarchive` — affected >=3.0.0 <3.6.1-r2
- Alpine:v3.22: `libarchive` — affected >=3.0.0 <3.6.1-r2
- Alpine:v3.23: `libarchive` — affected >=3.0.0 <3.6.1-r2
- Alpine:v3.24: `libarchive` — affected >=3.0.0 <3.6.1-r2

## Details
In libarchive before 3.6.2, the software does not check for an error after calling calloc function that can return with a NULL pointer if the function fails, which leads to a resultant NULL pointer dereference. NOTE: the discoverer cites this CWE-476 remark but third parties dispute the code-execution impact: "In rare circumstances, when NULL is equivalent to the 0x0 memory address and privileged code can access it, then writing or reading memory is possible, which may lead to code execution."

## References
- https://security.alpinelinux.org/vuln/CVE-2022-36227
