# [C] CVE-2019-7321

## Summary
Severity: Critical
Advisory: CVE-2019-7321
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-13
Source: https://osv.dev/vulnerability/CVE-2019-7321
Type: osv

## Details
Usage of an uninitialized variable in the function fz_load_jpeg in Artifex MuPDF 1.14 can result in a heap overflow vulnerability that allows an attacker to execute arbitrary code.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=700560
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=2be83b57e77938fddbb06bdffb11979ad89a9c7d
- https://github.com/ereisr00/bagofbugz/tree/master/MuPDF/700560
