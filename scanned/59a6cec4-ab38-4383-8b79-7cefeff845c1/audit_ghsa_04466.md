# [M] MessagePack-CSharp: Typeless deserialization type restrictions do not recurse into arrays or generic arguments

## Summary
Severity: Medium
Advisory: GHSA-qhmf-xw27-6rqr
CVE: CVE-2026-48517
CWE: CWE-470, CWE-502
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-qhmf-xw27-6rqr
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=0 <2.5.301
- NuGet: `MessagePack` — affected >=3.0 <3.1.7

## Details
## Summary

MessagePack-CSharp's typeless deserialization includes `MessagePackSerializerOptions.ThrowIfDeserializingTypeIsDisallowed(Type)` as a safety check for dangerous types. The default implementation checks the outer type name, but it does not recursively inspect array element types or generic type arguments.

As a result, a type that would be blocked directly can be wrapped inside an array or constructed generic type and pass the outer type check. The formatter machinery can then materialize formatters for the inner blocked type.

## Impact

Applications are affected when they deserialize untrusted payloads using typeless serialization features such as `MessagePackSerializer.Typeless`, `TypelessObjectResolver`, or related typeless resolver options.

Typeless deserialization is already a high-risk feature for untrusted data, but the presence of a disallowed-type hook creates an expectation that blocked types remain blocked. This issue weakens that mitigation because the check is not applied structurally to nested type components. An attacker who can supply typeless ext-100 payloads may bypass exact outer-type blocklist checks by naming wrapper types such as arrays or generic containers.

The consequence depends on which type is reached and what the application allows typeless deserialization to instantiate. The original findings describe bypasses involving blocked or user-blocklisted gadget types.

## Affected components

- Package: `MessagePack`
- Feature: typeless deserialization
- APIs: `MessagePackSerializerOptions.ThrowIfDeserializingTypeIsDisallowed`, `TypelessFormatter`
- Finding IDs: `MESSAGEPACKCSHARP-030`, duplicate/open variant `MESSAGEPACKCSHARP-OPEN-007`

## Patches

Fixes are available via versions 2.5.301 and 3.1.7.

Upgrade guidance:

1. Upgrade `MessagePack` to the patched version for your release line.
2. Upgrade companion MessagePack packages in the same dependency graph to the coordinated patched versions.

The fix should apply type-disallow checks recursively to array element types, pointer/byref element types where applicable, nullable underlying types, and constructed generic type arguments. Formatter paths that materialize types supplied by the wire should not instantiate inner types that fail the configured policy.

## Workarounds

Patching is recommended.

Avoid typeless deserialization for untrusted data. If typeless support is unavoidable, configure an explicit allowlist that rejects any type not approved by the application and ensure the allowlist recursively validates array elements and generic arguments. Do not rely on exact outer-type blocklists as a complete security boundary.

## Resources

- `MESSAGEPACKCSHARP-030`: typeless disallowed-type check is not recursive
- `MESSAGEPACKCSHARP-OPEN-007`: duplicate/open finding for typeless blocklist gaps
- CWE-502: Deserialization of Untrusted Data
- CWE-470: Use of Externally-Controlled Input to Select Classes or Code

## CVE split rationale

This vulnerability is independently fixable in typeless type-policy enforcement. It is separate from MVC default options, collection allocation, LZ4 decoding, and recursion-depth issues.

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-qhmf-xw27-6rqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-48517
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
