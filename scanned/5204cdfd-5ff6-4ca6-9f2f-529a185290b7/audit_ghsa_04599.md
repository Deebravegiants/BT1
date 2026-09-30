# [H]  MessagePack's LZ4 decompression may fail with AccessViolationException after dereferencing memory from bad input

## Summary
Severity: High
Advisory: GHSA-hv8m-jj95-wg3x
CVE: CVE-2026-48109
CWE: CWE-20
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-hv8m-jj95-wg3x
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=0 <2.5.301
- NuGet: `MessagePack` — affected >=3.0.214-rc.1 <3.1.7

## Details
### Impact

A vulnerability exists in the optional LZ4 decompression path used by MessagePack compression modes `Lz4Block` and `Lz4BlockArray`.

The decoder implementation is based on a deprecated fast-decompression algorithm that does not take a source-length bound. A remote attacker can send a crafted MessagePack payload with manipulated LZ4 token/length fields to force out-of-bounds reads from the compressed input buffer. In affected environments, this can trigger an `AccessViolationException` during decompression, causing process termination (denial of service). Under some conditions, limited unintended memory disclosure from over-read data may also be possible before failure.

This issue affects applications that deserialize untrusted data while LZ4 compression is enabled.

### Patches

The v2 versions are patched as of 2.5.301.
The v3 versions are patched as of 3.1.7.

### Workarounds

Instead of upgrading, an application may take the following precautions:

1. Disable LZ4 compression for untrusted input paths (`Lz4Block`, `Lz4BlockArray`).
2. Only accept compressed payloads from strongly trusted producers.
3. Isolate deserialization in a separate process/container with restart supervision to limit availability impact.

### Resources

- MESSAGEPACKCSHARP-010

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-hv8m-jj95-wg3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-48109
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
