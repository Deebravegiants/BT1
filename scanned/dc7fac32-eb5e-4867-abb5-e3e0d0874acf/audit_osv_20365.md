# [M] CVE-2021-33294

## Summary
Severity: Medium
Advisory: CVE-2021-33294
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-07-18
Source: https://osv.dev/vulnerability/CVE-2021-33294
Type: osv

## Details
In elfutils 0.183, an infinite loop was found in the function handle_symtab in readelf.c .Which allows attackers to cause a denial of service (infinite loop) via crafted file.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=27501
- https://sourceware.org/pipermail/elfutils-devel/2021q1/003607.html
