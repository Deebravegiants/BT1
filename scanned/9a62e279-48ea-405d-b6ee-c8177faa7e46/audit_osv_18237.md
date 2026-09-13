# [H] CVE-2020-25465

## Summary
Severity: High
Advisory: CVE-2020-25465
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-04
Source: https://osv.dev/vulnerability/CVE-2020-25465
Type: osv

## Details
Null Pointer Dereference. in xObjectBindingFromExpression at moddable/xs/sources/xsSyntaxical.c:3419 in Moddable SDK before OS200908 causes a denial of service (SEGV).

## References
- https://github.com/Moddable-OpenSource/moddable/releases/tag/OS200908
- https://github.com/Moddable-OpenSource/moddable/issues/442
