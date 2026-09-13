# [C] CVE-2019-16366

## Summary
Severity: Critical
Advisory: CVE-2019-16366
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-16
Source: https://osv.dev/vulnerability/CVE-2019-16366
Type: osv

## Details
In XS 9.0.0 in Moddable SDK OS180329, there is a heap-based buffer overflow in fxBeginHost in xsAPI.c when called from fxRunDefine in xsRun.c, as demonstrated by crafted JavaScript code to xst.

## References
- https://github.com/Moddable-OpenSource/moddable/issues/235
