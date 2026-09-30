# [H] MessagePack-CSharp: MessagePackReader.Skip can recurse without enforcing maximum object graph depth

## Summary
Severity: High
Advisory: GHSA-vh6j-jc39-fggf
CVE: CVE-2026-48506
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-vh6j-jc39-fggf
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=0 <2.5.301
- NuGet: `MessagePack` — affected >=3.0 <3.1.7

## Details
## Summary

`MessagePackReader.TrySkip()` recursively descends into nested arrays and maps without incrementing the reader depth or calling the configured depth checks. This bypasses `MessagePackSecurity.MaximumObjectGraphDepth`, the library's documented protection against deeply nested object graphs.

Many generated and dynamic formatters call `reader.Skip()` when they encounter unknown map keys, unknown array members, ignored fields, or data that should be skipped for forward compatibility. A deeply nested value in one of these skipped positions can therefore cause unbounded recursion and an uncatchable `StackOverflowException`.

## Impact

Applications that deserialize untrusted MessagePack payloads are affected when a formatter skips attacker-controlled values. This is a broad deserialization path and can be reached during normal object deserialization when an input includes an unknown member or extra value.

The attacker does not need to target a special resolver or compression mode. A payload containing many nested single-element arrays or maps in a skipped location can exhaust the process stack. Because `StackOverflowException` is not catchable in normal .NET execution, this terminates the host process and can deny service to other users of the same process.

`MessagePackSecurity.UntrustedData` does not mitigate this issue because the skip path does not participate in depth accounting.

## Affected components

- Package: `MessagePack`
- APIs: `MessagePackReader.Skip`, `MessagePackReader.TrySkip`, and formatter paths that skip unknown or ignored values
- Finding IDs: `MESSAGEPACKCSHARP-021`, duplicate/open variant `MESSAGEPACKCSHARP-OPEN-001`

## Patches

Fixes are prepared and will be released in coordinated patch versions.

Upgrade guidance:

1. Upgrade `MessagePack` to the patched version for your release line.
2. Upgrade companion MessagePack packages in the same dependency graph to the coordinated patched versions.

The fix should either make skip traversal iterative or apply the existing depth accounting to arrays and maps encountered by `TrySkip()`. Any exceeded depth limit should result in a catchable serialization exception instead of process stack exhaustion.

## Workarounds

Patching is recommended.

There is no complete workaround for applications that deserialize untrusted MessagePack payloads with affected versions. Reducing accepted message sizes can raise the cost of exploitation but does not remove the recursive skip behavior. Strict schema validation outside MessagePack-CSharp may help only if it rejects unknown or skipped fields before the serializer sees them.

## Resources

- `MESSAGEPACKCSHARP-021`: unbounded recursion in `TrySkip()`
- `MESSAGEPACKCSHARP-OPEN-001`: duplicate/open finding for the same root cause
- CWE-674: Uncontrolled Recursion

## CVE split rationale

This vulnerability is independently fixable in the skip traversal implementation. It should be tracked separately from formatter-specific missing depth checks, JSON conversion recursion, and non-recursion allocation bugs.

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-vh6j-jc39-fggf
- https://nvd.nist.gov/vuln/detail/CVE-2026-48506
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
