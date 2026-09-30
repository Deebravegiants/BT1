# [M] CVE-2021-34340

## Summary
Severity: Medium
Advisory: CVE-2021-34340
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2021-34340
Type: osv

## Details
Ming 0.4.8 has an out-of-bounds buffer access issue in the function decompileINCR_DECR() in decompiler.c file that causes a direct segmentation fault and leads to denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1969612
- https://github.com/libming/libming/issues/203
