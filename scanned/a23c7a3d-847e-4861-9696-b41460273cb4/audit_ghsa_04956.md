# [H] MessagePack-CSharp: Denial of service vulnerabilities can swamp the CPU or crash the process with stack and heap overflows

## Summary
Severity: High
Advisory: GHSA-382j-8mxh-c7x2
CVE: CVE-2026-48502
CWE: CWE-1188, CWE-125, CWE-190, CWE-407, CWE-409, CWE-470, CWE-502, CWE-674, CWE-789
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-382j-8mxh-c7x2
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=3.0 <3.1.7

## Details
## Summary

`MessagePackReader.ReadDateTime()` can allocate stack memory based on an attacker-controlled MessagePack extension length. In the slow path for timestamp extension parsing, the computed `tokenSize` includes the extension body length from the wire and is used in a `stackalloc` operation before the extension length is validated as one of the valid timestamp sizes.

A very small payload can claim a large timestamp extension body and cause a stack allocation large enough to trigger an uncatchable `StackOverflowException`, terminating the host process.

## Impact

Applications are affected when they deserialize untrusted payloads into types containing `DateTime` values. This path is available through the standard formatter set and does not require opting into typeless serialization, LZ4 compression, Unity-specific resolvers, or other specialized features.

`MessagePackSecurity.UntrustedData` and `MaximumObjectGraphDepth` do not mitigate this issue because the crash is caused by a single-frame stack allocation, not by object graph recursion.

An attacker can send a MessagePack timestamp extension header with an oversized body length and insufficient body bytes. The reader enters the slow path, attempts to stack-allocate a buffer sized from that declared length, and can terminate the process before a catchable serialization exception is thrown.

## Affected components

- Package: `MessagePack`
- API: `MessagePackReader.ReadDateTime`
- Data types: `DateTime` and formatter paths that call `ReadDateTime`
- Finding IDs: `MESSAGEPACKCSHARP-020`, related stack allocation finding `MESSAGEPACKCSHARP-CROW-MEM-001`

## Patches

Fixes are prepared and will be released in coordinated patch versions.

Upgrade guidance:

1. Upgrade `MessagePack` to the patched version for your release line.
2. Upgrade companion MessagePack packages in the same dependency graph to the coordinated patched versions.

The fix should validate timestamp extension lengths before any stack allocation. Valid MessagePack timestamp payload lengths are limited to the supported timestamp encodings, so oversized extension lengths should fail with a catchable MessagePack serialization exception before the slow path allocates a buffer.

## Workarounds

Patching is recommended.

Until a patched version is available, avoid deserializing untrusted MessagePack payloads into schemas that contain `DateTime` or `DateTimeOffset` values. Where possible, enforce strict maximum message sizes and reject malformed extension payloads before they reach MessagePack-CSharp.

There is no complete workaround for applications that must deserialize attacker-controlled MessagePack data containing date/time fields with affected versions.

## Resources

- `MESSAGEPACKCSHARP-020`: `ReadDateTime` stack allocation from attacker-controlled extension length
- `MESSAGEPACKCSHARP-CROW-MEM-001`: related attacker-controlled stack allocation finding in `MessagePackReader`
- CWE-770: Allocation of Resources Without Limits or Throttling

## CVE split rationale

This vulnerability is independently fixable in the DateTime extension parsing path by validating extension lengths before stack allocation. It is separate from recursive stack overflows, LZ4 issues, and collection allocation bugs.

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-382j-8mxh-c7x2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48502
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
