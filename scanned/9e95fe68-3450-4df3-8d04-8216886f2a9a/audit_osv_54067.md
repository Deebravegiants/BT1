# [M] CVE-2023-37837

## Summary
Severity: Medium
Advisory: CVE-2023-37837
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-07-13
Source: https://osv.dev/vulnerability/CVE-2023-37837
Type: osv

## Details
libjpeg commit db33a6e was discovered to contain a heap buffer overflow via LineBitmapRequester::EncodeRegion at linebitmaprequester.cpp. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted file.

## References
- https://github.com/thorfdbg/libjpeg/issues/87#BUG0
