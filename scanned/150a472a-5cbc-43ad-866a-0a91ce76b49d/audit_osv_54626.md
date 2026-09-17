# [H] CVE-2024-22749

## Summary
Severity: High
Advisory: CVE-2024-22749
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-25
Source: https://osv.dev/vulnerability/CVE-2024-22749
Type: osv

## Details
GPAC v2.3 was detected to contain a buffer overflow via the function gf_isom_new_generic_sample_description function in the isomedia/isom_write.c:4577

## References
- https://github.com/gpac/gpac/issues/2713
- https://github.com/hanxuer/crashes/blob/main/gapc/01/readme.md
