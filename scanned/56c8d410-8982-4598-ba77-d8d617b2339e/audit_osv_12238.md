# [H] CVE-2018-10972

## Summary
Severity: High
Advisory: CVE-2018-10972
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-10
Source: https://osv.dev/vulnerability/CVE-2018-10972
Type: osv

## Details
An issue was discovered in Free Lossless Image Format (FLIF) 0.3. The TransformPaletteC::process function in transform/palette_C.hpp allows remote attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact via a crafted file.

## References
- https://github.com/FLIF-hub/FLIF/issues/503
