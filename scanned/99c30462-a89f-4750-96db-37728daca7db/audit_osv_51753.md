# [M] CVE-2021-39519

## Summary
Severity: Medium
Advisory: CVE-2021-39519
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-39519
Type: osv

## Details
An issue was discovered in libjpeg through 2020021. A NULL pointer dereference exists in the function BlockBitmapRequester::PullQData() located in blockbitmaprequester.cpp It allows an attacker to cause Denial of Service.

## References
- https://github.com/thorfdbg/libjpeg/issues/28
