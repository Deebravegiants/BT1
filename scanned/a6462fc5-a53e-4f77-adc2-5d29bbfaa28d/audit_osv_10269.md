# [M] CVE-2017-14642

## Summary
Severity: Medium
Advisory: CVE-2017-14642
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14642
Type: osv

## Details
A NULL pointer dereference was discovered in the AP4_HdlrAtom class in Bento4 version 1.5.0-617. The vulnerability causes a segmentation fault and application crash in AP4_StdcFileByteStream::ReadPartial in System/StdC/Ap4StdCFileByteStream.cpp, which leads to remote denial of service.

## References
- https://blogs.gentoo.org/ago/2017/09/14/bento4-null-pointer-dereference-in-ap4_stdcfilebytestreamreadpartial-ap4stdcfilebytestream-cpp/
- https://github.com/axiomatic-systems/Bento4/commit/22192de5367fa0cee985917f092be4060b7c00b0
- https://github.com/axiomatic-systems/Bento4/issues/185
