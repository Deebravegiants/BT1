# [H] zstd-jni 1.3.8-4 through 1.5.7-13 Use-After-Free of Compression and Decompression Dictionaries

## Summary
Severity: High
Advisory: CVE-2026-87825
Aliases: GHSA-947w-pxjj-c7m9
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87825
Type: osv

## Details
zstd-jni before 1.5.7-14 contains a use-after-free vulnerability where streams and contexts hold a dictionary's shared lock only during the load call, allowing the dictionary to be closed while still referenced. Attackers can close a dictionary after associating it with a stream or context, causing subsequent read or write operations to access freed native memory, resulting in silent data corruption or JVM crashes.

## References
- https://repo1.maven.org/maven2/com/github/luben/zstd-jni/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87825.json
- https://github.com/luben/zstd-jni/releases/tag/v1.5.7-14
- https://github.com/luben/zstd-jni/security/advisories/GHSA-947w-pxjj-c7m9
- https://nvd.nist.gov/vuln/detail/CVE-2026-87825
- https://www.vulncheck.com/advisories/zstd-jni-1.3.8-4-through-1.5.7-13-use-after-free-of-compression-and-decompression-dictionaries
- https://github.com/luben/zstd-jni/commit/0827ed02551bbd8d6f8e4bbff99d83bf50f91938
- https://github.com/luben/zstd-jni/commit/393d7311766abbc285b149302c0fe1f94b16d555
- https://github.com/luben/zstd-jni/commit/a560131d7834598afd9cea6b7c107bc88e915936
- https://github.com/luben/zstd-jni
- https://github.com/luben/zstd-jni/blob/v1.5.7-13/src/main/java/com/github/luben/zstd/BaseZstdBufferDecompressingStreamNoFinalizer.java
- https://github.com/luben/zstd-jni/blob/v1.5.7-13/src/main/java/com/github/luben/zstd/ZstdInputStreamNoFinalizer.java
