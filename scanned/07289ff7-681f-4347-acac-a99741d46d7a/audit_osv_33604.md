# [M] CVE-2025-47256

## Summary
Severity: Medium
Advisory: CVE-2025-47256
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2025-05-06
Source: https://osv.dev/vulnerability/CVE-2025-47256
Type: osv

## Details
Libxmp through 4.6.2 has a stack-based buffer overflow in depack_pha in loaders/prowizard/pha.c via a malformed Pha format tracker module in a .mod file.

## References
- https://github.com/libxmp/libxmp/blob/ec22d1c7b93c8f681f8504a6c61c6f8a52458a10/src/loaders/prowizard/pha.c#L35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47256.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-47256
- https://github.com/libxmp/libxmp/issues/847
- https://github.com/GCatt-AS/CVE-2025-47256
