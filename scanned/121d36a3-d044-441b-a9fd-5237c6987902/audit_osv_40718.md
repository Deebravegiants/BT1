# [H] NanaZip: Heap out-of-bounds read in NanaZip SquashFS LZ4 decompressor via unchecked negative return value

## Summary
Severity: High
Advisory: CVE-2026-54616
Aliases: GHSA-95x5-qvvm-hmfp
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:L)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-54616
Type: osv

## Details
NanaZip is the 7-Zip derivative intended for the modern Windows experience. From version 1.0.88.0 until stable version 6.0.1698.0 and preview version 6.5.1742.0, the Lz4Decode function in NanaZip.Core/SevenZip/CPP/7zip/Archive/SquashfsHandler.cpp rejects only a zero return from LZ4_decompress_safe even though malformed input produces a negative error value. The negative int is converted to the unsigned SizeT destLen and then truncated into outBufWasWrittenSize, causing ReadBlock to trust an attacker-inflated _cachedUnpackBlockSize. During fragment extraction, an attacker-controlled inode Offset can make memcpy read beyond the _cachedBlock heap allocation and place adjacent heap contents in the extracted file, or crash the process. This issue is fixed in stable version 6.0.1698.0 and preview version 6.5.1742.0.

## References
- https://github.com/M2Team/NanaZip/releases/tag/6.0.1698.0
- https://github.com/M2Team/NanaZip/releases/tag/6.5.1742.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54616.json
- https://github.com/M2Team/NanaZip/security/advisories/GHSA-95x5-qvvm-hmfp
- https://nvd.nist.gov/vuln/detail/CVE-2026-54616
- https://github.com/M2Team/NanaZip/commit/733e8570d2ba96c3e52aab44f5fd886775d5952f
- https://github.com/M2Team/NanaZip/commit/ce0322a1932e16a53e4a13e48bc61804c7826956
