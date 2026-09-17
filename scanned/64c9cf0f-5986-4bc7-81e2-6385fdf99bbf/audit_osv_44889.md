# [H] zstd-jni 1.3.8-4 through 1.5.7-13 Use-After-Free via Setters Called After close()

## Summary
Severity: High
Advisory: CVE-2026-87877
Aliases: GHSA-2jw3-mg7f-vw4q
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87877
Type: osv

## Details
zstd-jni versions before 1.5.7-14 fail to validate closed state in setDict, setLongMax, setLevel and setRefMultipleDDicts methods of stream classes. Attackers can call these methods on closed streams to write through freed native pointers, corrupting unrelated objects or crashing the JVM.

## References
- https://repo1.maven.org/maven2/com/github/luben/zstd-jni/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87877.json
- https://github.com/luben/zstd-jni/releases/tag/v1.5.7-14
- https://github.com/luben/zstd-jni/security/advisories/GHSA-2jw3-mg7f-vw4q
- https://nvd.nist.gov/vuln/detail/CVE-2026-87877
- https://www.vulncheck.com/advisories/zstd-jni-1.3.8-4-through-1.5.7-13-use-after-free-via-setters-called-after-close
- https://github.com/luben/zstd-jni/commit/0827ed02551bbd8d6f8e4bbff99d83bf50f91938
- https://github.com/luben/zstd-jni/commit/393d7311766abbc285b149302c0fe1f94b16d555
- https://github.com/luben/zstd-jni/commit/f38f9a1563113d96d0fc38baee543f7457dd8a8e
- https://github.com/luben/zstd-jni
- https://github.com/luben/zstd-jni/blob/v1.5.7-13/src/main/java/com/github/luben/zstd/BaseZstdBufferDecompressingStreamNoFinalizer.java
- https://github.com/luben/zstd-jni/blob/v1.5.7-13/src/main/java/com/github/luben/zstd/ZstdInputStreamNoFinalizer.java
