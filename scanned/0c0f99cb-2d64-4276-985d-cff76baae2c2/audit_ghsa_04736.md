# [M] MessagePack-CSharp: Unity unsafe blit formatter allocates from unbounded byte length

## Summary
Severity: Medium
Advisory: GHSA-w567-gjr2-hm5j
CVE: CVE-2026-48514
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-w567-gjr2-hm5j
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=0 <2.5.301
- NuGet: `MessagePack` — affected >=3.0 <3.1.7

## Details
## Summary

`UnsafeBlitFormatterBase<T>.Deserialize` reads an attacker-controlled `byteLength` from an extension payload and allocates an array based on that value before validating it against the extension header length or remaining payload bytes.

The outer extension header is bounded by available input, but that bound is not used to constrain the inner `byteLength` before allocation. A very small payload can therefore request a very large `T[]` allocation.

## Impact

Applications are affected when they deserialize untrusted payloads using Unity blit resolvers such as `UnityBlitResolver` or `UnityBlitWithPrimitiveArrayResolver`.

This is especially relevant to Unity multiplayer clients or servers that use MessagePack-CSharp for networked values such as vectors, matrices, or primitive arrays. A hostile peer can send an extension payload with a large declared byte length and cause an out-of-memory exception or process termination on memory-constrained platforms.

The resolver is opt-in, but the vulnerable value is pure wire input and the allocation happens before the formatter verifies that the declared bytes are actually present in the extension body.

## Affected components

- Package: `MessagePack.UnityClient`
- Resolvers: `UnityBlitResolver`, `UnityBlitWithPrimitiveArrayResolver`
- API: `UnsafeBlitFormatterBase<T>.Deserialize`
- Finding IDs: `MESSAGEPACKCSHARP-080`, duplicate/open variant `MESSAGEPACKCSHARP-OPEN-010`

## Patches

Fixes are prepared and will be released in coordinated patch versions.

Upgrade guidance:

1. Upgrade `MessagePack.UnityClient` to the patched version for your release line.
2. Upgrade companion MessagePack packages in the same dependency graph to the coordinated patched versions.

The fix should validate `byteLength` before allocation. It should reject negative lengths, lengths greater than the extension body length after metadata, and lengths that are not a valid multiple of the element size.

## Workarounds

Patching is recommended.

Until a patched version is available, do not use Unity blit resolvers on data received from untrusted peers. Use safer resolvers or explicitly validate and size-limit messages before deserialization.

## Resources

- `MESSAGEPACKCSHARP-080`: unsafe blit formatter allocation from unbounded byte length
- `MESSAGEPACKCSHARP-OPEN-010`: duplicate/open finding for the same root cause
- CWE-770: Allocation of Resources Without Limits or Throttling

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-w567-gjr2-hm5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-48514
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
