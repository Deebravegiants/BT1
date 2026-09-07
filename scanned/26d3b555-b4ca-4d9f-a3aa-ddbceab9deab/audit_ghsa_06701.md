# [M] LZ4 Java: Native XXHash implementations can crash the JVM when passed invalid byte array ranges

## Summary
Severity: Medium
Advisory: GHSA-xx22-p4ch-683r
CVE: CVE-2026-59949
CWE: CWE-125, CWE-476
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-xx22-p4ch-683r
Type: github-advisory

## Affected
- Maven: `at.yawk.lz4:lz4-java` — affected >=0 <1.11.1
- Maven: `org.lz4:lz4-java` — affected >=0

## Details
### Summary

Insufficient validation of byte array arguments in JNI-based XXHash implementations in lz4-java 1.11.0 and earlier allows callers to crash the JVM by passing an invalid array reference or invalid range to native XXHash methods.

This affects applications where an attacker can influence the byte array object or the `off` / `len` arguments passed to affected XXHash APIs. It does **not** affect the common case where only the contents of a valid byte array are attacker-controlled.

Java-based XXHash implementations are *not* affected.

### Details

The JNI-backed XXHash implementations pass caller-provided byte array arguments to native code. The affected APIs are:

- `XXHashFactory.nativeInstance().hash32().hash(byte[] buf, int off, int len, int seed)`
- `XXHashFactory.nativeInstance().hash64().hash(byte[] buf, int off, int len, long seed)`
- `XXHashFactory.nativeInstance().newStreamingHash32(seed).update(byte[] bytes, int off, int len)`
- `XXHashFactory.nativeInstance().newStreamingHash64(seed).update(byte[] bytes, int off, int len)`

Before the fix, the streaming JNI implementations did not validate `bytes`, `off`, or `len` before calling `XXHashJNI.XXH32_update` / `XXHashJNI.XXH64_update`. The non-streaming JNI implementations called `SafeUtils.checkRange`, but `SafeUtils.checkRange(byte[], int, int)` skipped all array access when `len == 0`, so a null byte array with a zero length could still reach JNI.

As a result:

- `hash(null, 0, 0, seed)` and `update(null, 0, 0)` could pass a null array reference to JNI, causing a fatal JVM crash in `GetPrimitiveArrayCritical`.
- `update(new byte[16], 0, Integer.MAX_VALUE)` could cause native XXHash code to read far beyond the end of the Java array, causing a fatal JVM crash and potentially exposing in-process memory to the native routine before the crash.

The oversized-length non-streaming `hash(new byte[16], 0, Integer.MAX_VALUE, seed)` case was already rejected in Java before this fix. The missing validation affected the streaming oversized-length case and the zero-length null-array case for both streaming and non-streaming JNI XXHash APIs.

The impact of this vulnerability depends on how user code uses the XXHash API. Code that hashes attacker-controlled byte contents in a valid, correctly bounded array is not affected. Code may be affected if an attacker can cause the application to pass a null array, an attacker-controlled offset, or an attacker-controlled length to the native XXHash API. The primary impact is denial of service due to JVM termination. For oversized lengths, native code may also read outside the Java array before the process crashes.

### Mitigation

lz4-java 1.11.1 fixes this issue without requiring changes in user code.

If you cannot upgrade, avoid passing attacker-controlled array references, offsets, or lengths to JNI-backed XXHash APIs. In particular, validate that arrays are non-null and that `off` and `len` describe a range fully contained in the array before calling native XXHash methods.

Using `XXHashFactory.safeInstance()` avoids the JNI boundary and is not affected by this native crash behavior.

## References
- https://github.com/yawkat/lz4-java/security/advisories/GHSA-xx22-p4ch-683r
- https://github.com/yawkat/lz4-java/commit/dbd86d04b8dd716e1c2bc626be54189997d910da
- https://github.com/yawkat/lz4-java
- https://github.com/yawkat/lz4-java/releases/tag/v1.11.1
