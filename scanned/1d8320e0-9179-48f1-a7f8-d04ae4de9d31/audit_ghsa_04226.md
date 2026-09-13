# [M] MessagePack-CSharp: JSON conversion APIs can recurse without consistent depth enforcement

## Summary
Severity: Medium
Advisory: GHSA-cj9g-3mj2-g8vv
CVE: CVE-2026-48512
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-cj9g-3mj2-g8vv
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=0 <2.5.301
- NuGet: `MessagePack` — affected >=3.0 <3.1.7

## Details
## Summary

MessagePack-CSharp's JSON conversion helpers contain multiple recursion paths that do not consistently enforce a depth limit. These paths are in the JSON conversion component rather than normal typed MessagePack deserialization.

Three related issues are covered by this advisory:

1. `MessagePackSerializer.ConvertFromJson` recursively processes nested JSON arrays and objects in `FromJsonCore()` without consulting `MessagePackSecurity.MaximumObjectGraphDepth`.
2. `TinyJsonReader.ReadNextToken()` recursively consumes comma and colon separator characters, allowing even malformed JSON with long separator runs to consume one stack frame per character.
3. `MessagePackSerializer.ConvertToJson` applies depth checks to arrays and maps, but the typeless extension branch for ext-100 recursively calls `ToJsonCore()` without applying `MessagePackSecurity.DepthStep(ref reader)`.

Each path can allow attacker-controlled input to exhaust the process stack and trigger an uncatchable `StackOverflowException` instead of failing with a catchable parse or serialization exception.

## Impact

Applications are affected when they call MessagePack-CSharp JSON conversion APIs on attacker-controlled data. This includes gateways, diagnostics endpoints, migration tools, logging paths, and services that convert between external JSON and MessagePack payloads.

For JSON-to-MessagePack conversion, deeply nested JSON arrays or objects can recurse through `FromJsonCore()` without applying the configured object graph depth limit. Separately, long runs of comma or colon separator characters can recurse through `TinyJsonReader.ReadNextToken()` before normal structural validation rejects the input.

For MessagePack-to-JSON conversion, nested typeless extension wrappers can recurse through `ToJsonCore()` without the depth guard that the same function applies to arrays and maps.

`MessagePackSecurity.UntrustedData` does not fully mitigate these conversion paths because the missing checks occur inside JSON conversion and tokenization branches that do not consistently use the configured depth policy.

## Affected components

- Package: `MessagePack`
- APIs: `MessagePackSerializer.ConvertFromJson`, `MessagePackSerializer.ConvertToJson`
- Internal routines: `FromJsonCore`, `ToJsonCore`, `TinyJsonReader.ReadNextToken`
- Data shapes: deeply nested JSON arrays/objects, long JSON separator runs, and nested typeless MessagePack extension values converted to JSON
- Finding IDs: `MESSAGEPACKCSHARP-090`, `MESSAGEPACKCSHARP-091`, `MESSAGEPACKCSHARP-092`

## Patches

Fixes are prepared and will be released in coordinated patch versions.

Upgrade guidance:

1. Upgrade `MessagePack` to the patched version for your release line.
2. Upgrade companion MessagePack packages in the same dependency graph to the coordinated patched versions.

The JSON-to-MessagePack fix should add explicit JSON nesting-depth accounting to `FromJsonCore`, using the configured maximum object graph depth or an equivalent limit, or rewrite the conversion to use an iterative bounded stack.

The tokenizer fix should replace separator self-recursion in `TinyJsonReader.ReadNextToken()` with an iterative loop so consecutive commas, colons, and whitespace do not consume stack frames.

The MessagePack-to-JSON fix should apply `DepthStep` and matching `reader.Depth--` cleanup around recursive `ToJsonCore()` calls made from the typeless extension branch, consistent with the existing array and map conversion branches.

## Workarounds

Patching is recommended.

Until a patched version is available, do not pass untrusted JSON directly to `ConvertFromJson`, and do not call `ConvertToJson` on untrusted MessagePack payloads that may contain typeless extension values. Validate JSON nesting depth with a parser that enforces depth limits before calling MessagePack-CSharp, reject malformed JSON before conversion, and apply strict input-size limits.

Input-size limits reduce exposure but do not remove the recursive behavior in affected versions.

## References

- `MESSAGEPACKCSHARP-090`: `ConvertFromJson` unbounded structural recursion
- `MESSAGEPACKCSHARP-091`: `TinyJsonReader.ReadNextToken` separator self-recursion
- `MESSAGEPACKCSHARP-092`: `ConvertToJson` ext-100 branch missing depth enforcement
- CWE-674: Uncontrolled Recursion

## CVE split rationale

These issues are grouped because they affect the same JSON conversion feature area and share the same failure mode: recursive conversion/tokenization paths do not consistently enforce depth or iteration bounds for attacker-controlled input. They are distinct from normal binary MessagePack skip recursion, dynamic union formatter depth accounting, DateTime stack allocation, and allocation-oriented denial-of-service issues.

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-cj9g-3mj2-g8vv
- https://nvd.nist.gov/vuln/detail/CVE-2026-48512
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
