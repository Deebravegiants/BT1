# [H] CVE-2017-14646

## Summary
Severity: High
Advisory: CVE-2017-14646
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-14646
Type: osv

## Details
The AP4_AvccAtom and AP4_HvccAtom classes in Bento4 version 1.5.0-617 do not properly validate data sizes, leading to a heap-based buffer over-read and application crash in AP4_DataBuffer::SetData in Core/Ap4DataBuffer.cpp.

## References
- https://blogs.gentoo.org/ago/2017/09/14/bento4-heap-based-buffer-overflow-in-ap4_databuffersetdata-ap4databuffer-cpp/
- https://github.com/axiomatic-systems/Bento4/commit/53499d8d4c69142137c7c7f0097a444783fdeb90
- https://github.com/axiomatic-systems/Bento4/issues/188
