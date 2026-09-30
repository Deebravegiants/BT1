# [H] CVE-2019-8378

## Summary
Severity: High
Advisory: CVE-2019-8378
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-17
Source: https://osv.dev/vulnerability/CVE-2019-8378
Type: osv

## Details
An issue was discovered in Bento4 1.5.1-628. A heap-based buffer over-read exists in AP4_BitStream::ReadBytes() in Codecs/Ap4BitStream.cpp, a similar issue to CVE-2017-14645. It can be triggered by sending a crafted file to the aac2mp4 binary. It allows an attacker to cause a Denial of Service (Segmentation fault) or possibly have unspecified other impact.

## References
- https://github.com/axiomatic-systems/Bento4/issues/363
- https://research.loginsoft.com/bugs/a-heap-buffer-overflow-vulnerability-in-the-function-ap4_bitstreamreadbytes-bento4-1-5-1-628/
