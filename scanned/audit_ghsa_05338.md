# [M] MessagePack-CSharp: InterfaceLookupFormatter bypasses collision-resistant comparer settings

## Summary
Severity: Medium
Advisory: GHSA-q2h6-ghwm-5qm8
CVE: CVE-2026-48516
CWE: CWE-407
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-q2h6-ghwm-5qm8
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=0 <2.5.301
- NuGet: `MessagePack` — affected >=3.0 <3.1.7

## Details
## Summary

`InterfaceLookupFormatter<TKey,TElement>` constructs an internal `Dictionary<TKey, IGrouping<TKey,TElement>>` with the default equality comparer instead of the security-aware comparer supplied by `options.Security.GetEqualityComparer<TKey>()`.

Other hash-based collection formatters use the security-aware comparer when `MessagePackSecurity.UntrustedData` is configured. This formatter omission allows hash-collision CPU denial of service against `ILookup<TKey,TElement>` even when the application has opted into the untrusted-data security posture.

## Impact

Applications are affected when they deserialize untrusted payloads into schemas containing `ILookup<TKey,TElement>` with a key type for which attacker-controlled hash collisions are feasible.

Under the default comparer, many colliding keys can degrade dictionary insertion from amortized constant time to quadratic behavior. A payload of colliding keys can consume CPU for a disproportionate amount of time. This bypasses the mitigation that developers intentionally enabled by using `MessagePackSecurity.UntrustedData`.

## Affected components

- Package: `MessagePack`
- API: `InterfaceLookupFormatter<TKey,TElement>.Create`
- Data type: `ILookup<TKey,TElement>`
- Finding ID: `MESSAGEPACKCSHARP-041`

## Patches

Fixes are prepared and will be released in coordinated patch versions.

Upgrade guidance:

1. Upgrade `MessagePack` to the patched version for your release line.
2. Upgrade companion MessagePack packages in the same dependency graph to the coordinated patched versions.

The fix should create the internal dictionary with `options.Security.GetEqualityComparer<TKey>()`, matching the sibling dictionary and lookup formatter behavior.

## Workarounds

Patching is recommended.

Until a patched version is available, avoid exposing `ILookup<TKey,TElement>` in DTOs that deserialize untrusted data. Use collection shapes that are already protected by the security-aware comparer path, or validate and cap collection sizes at the transport boundary.

## Resources

- `MESSAGEPACKCSHARP-041`: `InterfaceLookupFormatter` missing security comparer
- CWE-407: Inefficient Algorithmic Complexity

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-q2h6-ghwm-5qm8
- https://nvd.nist.gov/vuln/detail/CVE-2026-48516
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
