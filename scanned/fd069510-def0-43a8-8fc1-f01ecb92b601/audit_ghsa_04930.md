# [M] MessagePack-CSharp: LZ4 decompression allocates from unbounded declared output lengths

## Summary
Severity: Medium
Advisory: GHSA-v72x-2h86-7f8m
CVE: CVE-2026-48510
CWE: CWE-409, CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-v72x-2h86-7f8m
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=0 <2.5.301
- NuGet: `MessagePack` — affected >=3.0 <3.1.7

## Details
## Summary

When MessagePack-CSharp decompresses `Lz4Block` or `Lz4BlockArray` payloads, it reads declared uncompressed lengths from the wire and allocates output buffers based on those lengths before validating that the compressed data is valid or that the declared expansion is reasonable.

A small payload can claim a very large uncompressed length and force a large allocation before LZ4 decoding begins.

## Impact

Applications are affected when they deserialize attacker-controlled MessagePack payloads with `MessagePackCompression.Lz4Block` or `MessagePackCompression.Lz4BlockArray` enabled.

In the `Lz4Block` case, an attacker-controlled integer is used to request the destination span. In the `Lz4BlockArray` case, per-block uncompressed lengths and their aggregate can be attacker-controlled. Without a cap, the declared output size can be disproportionate to the input size, producing out-of-memory exceptions, process termination on constrained hosts, or severe memory pressure.

This advisory is about unbounded allocation from declared decompressed sizes. It is separate from the LZ4 source-buffer over-read issue, which concerns unsafe decoder reads beyond the compressed input buffer.

## Affected components

- Package: `MessagePack`
- Feature: LZ4 compressed MessagePack payloads
- APIs: `MessagePackSerializer` with `WithCompression(MessagePackCompression.Lz4Block)` or `WithCompression(MessagePackCompression.Lz4BlockArray)`
- Internal routine: `MessagePackSerializer.TryDecompress`
- Finding ID: `MESSAGEPACKCSHARP-OPEN-004`

## Patches

Fixes are prepared and will be released in coordinated patch versions.

Upgrade guidance:

1. Upgrade `MessagePack` to the patched version for your release line.
2. Upgrade companion MessagePack packages in the same dependency graph to the coordinated patched versions.

The fix should reject negative and excessive uncompressed lengths before allocation. It should also cap aggregate decompressed size for block arrays and expose or honor an appropriate maximum decompressed length policy.

## Workarounds

Patching is recommended.

Until a patched version is available, do not enable MessagePack-CSharp's built-in LZ4 compression modes for untrusted inputs. If compression is required, enforce strict compressed and decompressed size limits outside MessagePack-CSharp before deserialization.

## Resources

- `MESSAGEPACKCSHARP-OPEN-004`: LZ4 decompression allocation from unbounded uncompressed length
- `MESSAGEPACKCSHARP-011`: duplicate decompression-bomb finding
- CWE-409: Improper Handling of Highly Compressed Data
- CWE-770: Allocation of Resources Without Limits or Throttling

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-v72x-2h86-7f8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-48510
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
