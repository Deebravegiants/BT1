# [M] CVE-2017-14638

## Summary
Severity: Medium
Advisory: CVE-2017-14638
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14638
Type: osv

## Details
AP4_AtomFactory::CreateAtomFromStream in Core/Ap4AtomFactory.cpp in Bento4 version 1.5.0-617 has missing NULL checks, leading to a NULL pointer dereference, segmentation fault, and application crash in AP4_Atom::SetType in Core/Ap4Atom.h.

## References
- https://blogs.gentoo.org/ago/2017/09/14/bento4-null-pointer-dereference-in-ap4_atomsettype-ap4atom-h/
- https://github.com/axiomatic-systems/Bento4/commit/be7185faf7f52674028977dcf501c6039ff03aa5
- https://github.com/axiomatic-systems/Bento4/issues/182
