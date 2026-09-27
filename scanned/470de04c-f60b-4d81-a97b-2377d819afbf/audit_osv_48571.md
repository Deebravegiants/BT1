# [H] CVE-2017-9670

## Summary
Severity: High
Advisory: CVE-2017-9670
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-15
Source: https://osv.dev/vulnerability/CVE-2017-9670
Type: osv

## Details
An uninitialized stack variable vulnerability in load_tic_series() in set.c in gnuplot 5.2.rc1 allows an attacker to cause Denial of Service (Segmentation fault and Memory Corruption) or possibly have unspecified other impact when a victim opens a specially crafted file.

## References
- https://sourceforge.net/p/gnuplot/bugs/1933/
