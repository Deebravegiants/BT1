# [H] CVE-2018-11100

## Summary
Severity: High
Advisory: CVE-2018-11100
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-15
Source: https://osv.dev/vulnerability/CVE-2018-11100
Type: osv

## Details
The decompileSETTARGET function in decompile.c in libming through 0.4.8 mishandles cases where the header indicates a file size greater than the actual size, which allows remote attackers to cause a denial of service (Segmentation fault and application crash) or possibly have unspecified other impact.

## References
- https://docs.google.com/document/d/1N-_obGIyAM5DGcrB7gHy89Oy68aDvxSMjrKaaM7KOFA/edit
- https://github.com/libming/libming/issues/142
