# [M] CVE-2023-51258

## Summary
Severity: Medium
Advisory: CVE-2023-51258
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-18
Source: https://osv.dev/vulnerability/CVE-2023-51258
Type: osv

## Details
A memory leak issue discovered in YASM v.1.3.0 allows a local attacker to cause a denial of service via the new_Token function in the modules/preprocs/nasm/nasm-pp:1512.

## References
- https://github.com/hanxuer/crashes/blob/main/yasm/04/readme.md
