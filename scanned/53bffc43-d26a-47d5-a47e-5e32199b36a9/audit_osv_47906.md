# [H] CVE-2017-14519

## Summary
Severity: High
Advisory: CVE-2017-14519
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-17
Source: https://osv.dev/vulnerability/CVE-2017-14519
Type: osv

## Details
In Poppler 0.59.0, memory corruption occurs in a call to Object::streamGetChar in Object.h after a repeating series of Gfx::display, Gfx::go, Gfx::execOp, Gfx::opShowText, and Gfx::doShowText calls (aka a Gfx.cc infinite loop).

## References
- https://www.debian.org/security/2018/dsa-4079
- https://bugs.freedesktop.org/show_bug.cgi?id=102701
