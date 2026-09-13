# [M] CVE-2020-21686

## Summary
Severity: Medium
Advisory: CVE-2020-21686
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-21686
Type: osv

## Details
A stack-use-after-scope issue discovered in expand_mmac_params function in preproc.c in nasm before 2.15.04 allows remote attackers to cause a denial of service via crafted asm file.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392643
