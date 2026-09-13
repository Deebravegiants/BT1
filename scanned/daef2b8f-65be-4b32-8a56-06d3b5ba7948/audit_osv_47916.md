# [H] CVE-2017-14929

## Summary
Severity: High
Advisory: CVE-2017-14929
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-30
Source: https://osv.dev/vulnerability/CVE-2017-14929
Type: osv

## Details
In Poppler 0.59.0, memory corruption occurs in a call to Object::dictLookup() in Object.h after a repeating series of Gfx::display, Gfx::go, Gfx::execOp, Gfx::opFill, Gfx::doPatternFill, Gfx::doTilingPatternFill and Gfx::drawForm calls (aka a Gfx.cc infinite loop), a different vulnerability than CVE-2017-14519.

## References
- https://www.debian.org/security/2018/dsa-4097
- https://bugs.freedesktop.org/show_bug.cgi?id=102969
