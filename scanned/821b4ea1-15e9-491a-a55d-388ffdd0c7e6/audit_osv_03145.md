# [H] ALPINE-CVE-2024-53427

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-53427
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-53427
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.0-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.0-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.0-r0

## Details
decNumberCopy in decNumber.c in jq through 1.7.1 does not properly consider that NaN is interpreted as numeric, which has a resultant stack-based buffer overflow and out-of-bounds write, as demonstrated by use of --slurp with subtraction, such as a filter of .-. when the input has a certain form of digit string with NaN (e.g., "1 NaN123" immediately followed by many more digits).

## References
- https://security.alpinelinux.org/vuln/CVE-2024-53427
