# [M] CVE-2019-7699

## Summary
Severity: Medium
Advisory: CVE-2019-7699
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-10
Source: https://osv.dev/vulnerability/CVE-2019-7699
Type: osv

## Details
A heap-based buffer over-read occurs in AP4_BitStream::WriteBytes in Codecs/Ap4BitStream.cpp in Bento4 v1.5.1-627. Remote attackers could leverage this vulnerability to cause an exception via crafted mp4 input, which leads to a denial of service.

## References
- https://github.com/axiomatic-systems/Bento4/issues/355
