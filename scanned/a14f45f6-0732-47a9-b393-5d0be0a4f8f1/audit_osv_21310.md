# [H] CVE-2021-42006

## Summary
Severity: High
Advisory: CVE-2021-42006
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-10-04
Source: https://osv.dev/vulnerability/CVE-2021-42006
Type: osv

## Details
An out-of-bounds access in GffLine::GffLine in gff.cpp in GCLib 0.12.7 allows an attacker to cause a segmentation fault or possibly have unspecified other impact via a crafted GFF file.

## References
- https://github.com/gpertea/gclib/issues/11
