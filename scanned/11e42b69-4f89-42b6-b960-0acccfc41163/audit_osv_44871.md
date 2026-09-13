# [M] zstd-jni 1.2.0 through 1.5.7-13 Out-of-Bounds Read via ZstdDictCompress

## Summary
Severity: Medium
Advisory: CVE-2026-87795
Aliases: GHSA-ff36-7w3w-g8rm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87795
Type: osv

## Details
zstd-jni versions before 1.5.7-14 fail to validate offset and length parameters in the ZstdDictCompress constructor, allowing out-of-bounds memory reads. Attackers can supply untrusted offset or length values to read native heap memory into the compression dictionary, typically causing JVM crashes.

## References
- https://repo1.maven.org/maven2/com/github/luben/zstd-jni/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87795.json
- https://github.com/luben/zstd-jni/releases/tag/v1.5.7-14
- https://github.com/luben/zstd-jni/security/advisories/GHSA-ff36-7w3w-g8rm
- https://nvd.nist.gov/vuln/detail/CVE-2026-87795
- https://www.vulncheck.com/advisories/zstd-jni-1.2.0-through-1.5.7-13-out-of-bounds-read-via-zstddictcompress
- https://github.com/luben/zstd-jni/commit/0d64de4dee6606ff506be36c7f2e714ad0c80fdb
- https://github.com/luben/zstd-jni/commit/1c4e5a6c3ce8458095225d987d669e6a0937734a
- https://github.com/luben/zstd-jni
- https://github.com/luben/zstd-jni/blob/v1.5.7-13/src/main/java/com/github/luben/zstd/ZstdDictCompress.java
- https://github.com/luben/zstd-jni/blob/v1.5.7-13/src/main/native/jni_fast_zstd.c
