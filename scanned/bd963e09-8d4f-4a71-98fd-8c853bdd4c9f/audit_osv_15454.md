# [M] CVE-2019-16349

## Summary
Severity: Medium
Advisory: CVE-2019-16349
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-09-16
Source: https://osv.dev/vulnerability/CVE-2019-16349
Type: osv

## Details
Bento4 1.5.1-628 has a NULL pointer dereference in AP4_ByteStream::ReadUI32 in Core/Ap4ByteStream.cpp when called from the AP4_TrunAtom class.

## References
- https://github.com/axiomatic-systems/Bento4/issues/422
