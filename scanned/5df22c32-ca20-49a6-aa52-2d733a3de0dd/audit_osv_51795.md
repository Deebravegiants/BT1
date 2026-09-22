# [M] CVE-2021-40647

## Summary
Severity: Medium
Advisory: CVE-2021-40647
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-09-09
Source: https://osv.dev/vulnerability/CVE-2021-40647
Type: osv

## Details
In man2html 1.6g, a specific string being read in from a file will overwrite the size parameter in the top chunk of the heap. This at least causes the program to segmentation abort if the heap size parameter isn't aligned correctly. In version before GLIBC version 2.29 and aligned correctly, it allows arbitrary write anywhere in the programs memory.

## References
- https://gist.github.com/untaman/cb58123fe89fc65e3984165db5d40933
