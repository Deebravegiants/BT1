# [H] aircompressor Snappy and LZ4 Java-based decompressor implementation can leak information from reused output buffer

## Summary
Severity: High
Advisory: GHSA-vx9q-rhv9-3jvg
CVE: CVE-2025-67721
CWE: CWE-125, CWE-201
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-12
Source: https://github.com/advisories/GHSA-vx9q-rhv9-3jvg
Type: github-advisory

## Affected
- Maven: `io.airlift:aircompressor-v3` — affected >=0 <3.4
- Maven: `io.airlift:aircompressor` — affected >=0 <2.0.3

## Details
### Summary
Incorrect handling of malformed data in Java-based decompressor implementations for Snappy and LZ4 allows remote attackers to read previous buffer contents via crafted compressed input. In applications where the output buffer is reused without being cleared, this may lead to disclosure of sensitive data.

### Details
With certain crafted compressed inputs, elements from the output buffer can end up in the uncompressed output. This is relevant for applications that reuse the same output buffer to uncompress multiple inputs. This can be the case of a web server that allocates a fix-sized buffer for performance purposes. This is similar to [GHSA-cmp6-m4wj-q63q](https://github.com/yawkat/lz4-java/security/advisories/GHSA-cmp6-m4wj-q63q).

### Impact
Applications using aircompressor as described above may leak sensitive information to external unauthorized attackers.

### Mitigation

The vulnerability is fixed in release 3.4 and 2.0.3. However, it can be mitigated by either:
* Avoiding reuse of the decompression buffer across calls
* Clearing the decompression buffer before a call to decompress data

## References
- https://github.com/airlift/aircompressor/security/advisories/GHSA-vx9q-rhv9-3jvg
- https://nvd.nist.gov/vuln/detail/CVE-2025-67721
- https://github.com/airlift/aircompressor/pull/309
- https://github.com/airlift/aircompressor/commit/f2b489b398779b40c1ee29ddb11d7edef54ddc15
- https://github.com/airlift/aircompressor/commit/ff12c4d5757c9d6d1de3d39a10402f1f84f9b765
- https://github.com/airlift/aircompressor
- https://github.com/airlift/aircompressor/releases/tag/2.0.3
