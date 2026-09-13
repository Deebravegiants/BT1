# [M] CVE-2017-14640

## Summary
Severity: Medium
Advisory: CVE-2017-14640
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14640
Type: osv

## Details
A NULL pointer dereference was discovered in AP4_AtomSampleTable::GetSample in Core/Ap4AtomSampleTable.cpp in Bento4 version 1.5.0-617. The vulnerability causes a segmentation fault and application crash, which leads to remote denial of service.

## References
- https://blogs.gentoo.org/ago/2017/09/14/bento4-null-pointer-dereference-in-ap4_atomsampletablegetsample-ap4atomsampletable-cpp/
- https://github.com/axiomatic-systems/Bento4/commit/2f267f89f957088197f4b1fc254632d1645b415d
- https://github.com/axiomatic-systems/Bento4/issues/183
