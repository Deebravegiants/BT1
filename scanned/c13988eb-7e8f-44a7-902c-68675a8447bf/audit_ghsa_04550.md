# [M] MessagePack-CSharp: DynamicUnionResolver-generated deserializers miss depth enforcement

## Summary
Severity: Medium
Advisory: GHSA-wfr3-xj75-pfwh
CVE: CVE-2026-48513
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-wfr3-xj75-pfwh
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=0 <2.5.301
- NuGet: `MessagePack` — affected >=3.0 <3.1.7

## Details
## Summary

Runtime-generated union deserializers emitted by `DynamicUnionResolver` do not call `MessagePackSecurity.DepthStep(ref reader)` and do not decrement `reader.Depth` around recursive deserialization and skip paths.

This means union deserialization does not consistently participate in the maximum object graph depth enforcement that protects other recursive formatter paths. For unknown union keys, the emitted deserializer calls `reader.Skip()` on attacker-controlled data without an enclosing depth step.

## Impact

Applications are affected when they deserialize untrusted payloads into object graphs containing `[Union]`-decorated interfaces or abstract classes handled by `DynamicUnionResolver`.

An attacker can provide a union payload with an unknown key and a deeply nested value. Because the generated union formatter does not enter the depth accounting scope before skipping or recursively processing the value, configured depth limits can be bypassed. In combination with recursive skip behavior, this can terminate the process with an uncatchable `StackOverflowException`.

This issue is narrower than the general `TrySkip()` recursion issue because it specifically concerns a formatter-generation path that fails to count union nesting. It remains independently fixable because the emitted IL should mirror the depth-step behavior used by source-generated union formatters and dynamic object formatters.

## Affected components

- Package: `MessagePack`
- API: `DynamicUnionResolver.BuildDeserialize`
- Data types: `[Union]`-decorated interface and abstract class hierarchies handled by the dynamic resolver
- Finding ID: `MESSAGEPACKCSHARP-070`

## Patches

Fixes are prepared and will be released in coordinated patch versions.

Upgrade guidance:

1. Upgrade `MessagePack` to the patched version for your release line.
2. Upgrade companion MessagePack packages in the same dependency graph to the coordinated patched versions.

The fix should emit `DepthStep` and matching `reader.Depth--` cleanup in dynamic union deserializers, consistent with other recursive formatter implementations.

## Workarounds

Patching is recommended.

Until a patched version is available, avoid deserializing untrusted payloads into dynamically resolved `[Union]` types. Prefer source-generated formatters that include depth checks, where applicable, and enforce outer message-size and schema constraints.

## Resources

- `MESSAGEPACKCSHARP-070`: dynamic union deserializer missing depth-step enforcement
- CWE-674: Uncontrolled Recursion

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-wfr3-xj75-pfwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-48513
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
