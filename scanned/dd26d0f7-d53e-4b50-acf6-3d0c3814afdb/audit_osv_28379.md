# [M] ermig1979 Simd SimdMemoryStream.h ReadUnsigned heap-based overflow

## Summary
Severity: Medium
Advisory: CVE-2024-3207
CVSS: 5.5 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-02
Source: https://osv.dev/vulnerability/CVE-2024-3207
Type: osv

## Details
A vulnerability was found in ermig1979 Simd up to 6.0.134. It has been declared as critical. This vulnerability affects the function ReadUnsigned of the file src/Simd/SimdMemoryStream.h. The manipulation leads to heap-based buffer overflow. The exploit has been disclosed to the public and may be used. VDB-259054 is the identifier assigned to this vulnerability. NOTE: The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3207.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3207
- https://vuldb.com/?id.259054
- https://vuldb.com/?submit.304572
- https://vuldb.com/?ctiid.259054
- https://drive.google.com/drive/folders/1z0JBsZ-QR3RsuAf-uyit_ZGXCh0rEvFq?usp=sharing
