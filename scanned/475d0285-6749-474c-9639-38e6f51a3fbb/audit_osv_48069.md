# [C] CVE-2017-17821

## Summary
Severity: Critical
Advisory: CVE-2017-17821
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-21
Source: https://osv.dev/vulnerability/CVE-2017-17821
Type: osv

## Details
WTF/wtf/FastBitVector.h in WebKit, as distributed in Safari Technology Preview Release 46, allows remote attackers to cause a denial of service (buffer overflow) or possibly have unspecified other impact because it calls the FastBitVectorWordOwner::resizeSlow function (in WTF/wtf/FastBitVector.cpp) for a purpose other than initializing a bitvector size, and resizeSlow mishandles cases where the old array length is greater than the new array length.

## References
- https://github.com/dwfault/PoCs/blob/master/WebKit%20Misuse%20of%20WTF:wtf:FastBitVector%20result%20in%20potential%20BOF/WebKit%20Misuse%20of%20WTF:wtf:FastBitVector%20result%20in%20potential%20BOF.md
- https://bugs.webkit.org/show_bug.cgi?id=181020
