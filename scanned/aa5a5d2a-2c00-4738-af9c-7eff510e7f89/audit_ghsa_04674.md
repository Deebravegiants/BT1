# [M] MessagePack-CSharp: ExpandoObject formatter can perform quadratic insertion work on untrusted maps

## Summary
Severity: Medium
Advisory: GHSA-2x83-8g95-xh59
CVE: CVE-2026-48511
CWE: CWE-407
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-2x83-8g95-xh59
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=0 <2.5.301
- NuGet: `MessagePack` — affected >=3.0 <3.1.7

## Details
## Summary

`ExpandoObjectFormatter.Deserialize` populates `System.Dynamic.ExpandoObject` by calling `IDictionary<string, object>.Add` for each map entry. `ExpandoObject` internally maintains member names in array-like structures, so inserting many distinct keys can require repeated linear scans and array copies.

For large attacker-controlled maps, this produces quadratic CPU and allocation behavior. The issue is especially surprising because `ExpandoObjectResolver.Options` is configured with `MessagePackSecurity.UntrustedData`, but collision-resistant dictionary comparers cannot protect `ExpandoObject` insertion internals.

## Impact

Applications are affected when they deserialize untrusted MessagePack maps into `ExpandoObject` using `ExpandoObjectResolver` or related resolver options.

A hostile payload containing many distinct keys can cause CPU exhaustion and allocation churn disproportionate to the input size. This can make a server unresponsive or exhaust memory under concurrent request load.

This is not a hash-collision attack against a configurable dictionary comparer. The super-linear behavior comes from `ExpandoObject`'s insertion model, so `MessagePackSecurity.UntrustedData` does not eliminate the cost.

## Affected components

- Package: `MessagePack`
- APIs: `ExpandoObjectFormatter.Deserialize`, `ExpandoObjectResolver`
- Data type: `System.Dynamic.ExpandoObject`
- Finding ID: `MESSAGEPACKCSHARP-102`

## Patches

Fixes are prepared and will be released in coordinated patch versions.

Upgrade guidance:

1. Upgrade `MessagePack` to the patched version for your release line.
2. Upgrade companion MessagePack packages in the same dependency graph to the coordinated patched versions.

Potential fixes include applying a map-entry count limit for `ExpandoObject` under untrusted-data settings, buffering into a security-aware dictionary before materializing a bounded `ExpandoObject`, or otherwise rejecting maps large enough to trigger quadratic behavior.

## Workarounds

Patching is recommended.

Until a patched version is available, avoid deserializing untrusted payloads into `ExpandoObject`. Prefer strongly typed DTOs or dictionaries with security-aware comparers and explicit count limits. Enforce request-size and map-entry limits at the transport or application layer.

## Resources

- `MESSAGEPACKCSHARP-102`: `ExpandoObjectFormatter` quadratic insertion behavior
- CWE-407: Inefficient Algorithmic Complexity

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-2x83-8g95-xh59
- https://nvd.nist.gov/vuln/detail/CVE-2026-48511
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
