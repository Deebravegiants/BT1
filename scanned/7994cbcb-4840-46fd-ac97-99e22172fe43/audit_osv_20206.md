# [H] CVE-2021-32265

## Summary
Severity: High
Advisory: CVE-2021-32265
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32265
Type: osv

## Details
An issue was discovered in Bento4 through v1.6.0-637. A global-buffer-overflow exists in the function AP4_MemoryByteStream::WritePartial() located in Ap4ByteStream.cpp. It allows an attacker to cause code execution or information disclosure.

## References
- https://github.com/axiomatic-systems/Bento4/issues/545
