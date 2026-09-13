# [C] CVE-2023-52389

## Summary
Severity: Critical
Advisory: CVE-2023-52389
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-27
Source: https://osv.dev/vulnerability/CVE-2023-52389
Type: osv

## Details
UTF32Encoding.cpp in POCO has a Poco::UTF32Encoding integer overflow and resultant stack buffer overflow because Poco::UTF32Encoding::convert() and Poco::UTF32::queryConvert() may return a negative integer if a UTF-32 byte sequence evaluates to a value of 0x80000000 or higher. This is fixed in 1.11.8p2, 1.12.5p2, and 1.13.0.

## References
- https://github.com/pocoproject/poco/compare/poco-1.12.5p2-release...poco-1.13.0-release
- https://lists.debian.org/debian-lts-announce/2025/01/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52389.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52389
- https://github.com/pocoproject/poco/issues/4320
- https://pocoproject.org/blog/?p=1226
