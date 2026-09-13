# [H] CVE-2019-9878

## Summary
Severity: High
Advisory: CVE-2019-9878
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/CVE-2019-9878
Type: osv

## Details
There is an invalid memory access in the function GfxIndexedColorSpace::mapColorToBase() located in GfxState.cc in Xpdf 4.0.0, as used in pdfalto 0.2. It can be triggered by (for example) sending a crafted pdf file to the pdftops binary. It allows an attacker to cause Denial of Service (Segmentation fault) or possibly have unspecified other impact.

## References
- https://github.com/kermitt2/pdfalto/issues/46
- https://research.loginsoft.com/bugs/invalid-memory-access-in-gfxindexedcolorspacemapcolortobase-pdfalto-0-2/
