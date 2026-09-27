# [H] CVE-2017-6363

## Summary
Severity: High
Advisory: CVE-2017-6363
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2020-02-27
Source: https://osv.dev/vulnerability/CVE-2017-6363
Type: osv

## Details
In the GD Graphics Library (aka LibGD) through 2.2.5, there is a heap-based buffer over-read in tiffWriter in gd_tiff.c. NOTE: the vendor says "In my opinion this issue should not have a CVE, since the GD and GD2 formats are documented to be 'obsolete, and should only be used for development and testing purposes.'

## References
- https://github.com/libgd/libgd/issues/383
