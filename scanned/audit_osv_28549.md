# [M] CVE-2024-34408

## Summary
Severity: Medium
Advisory: CVE-2024-34408
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2024-34408
Type: osv

## Details
Tencent libpag through 4.3.51 has an integer overflow in DecodeStream::checkEndOfFile() in codec/utils/DecodeStream.cpp via a crafted PAG (Portable Animated Graphics) file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34408.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34408
- https://github.com/Tencent/libpag/issues/2230
- https://github.com/Tencent/libpag/pull/2243
