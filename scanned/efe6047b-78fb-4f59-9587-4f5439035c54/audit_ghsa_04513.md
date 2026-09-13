# [M] MessagePack-CSharp: Multi-dimensional array formatters allocate from unchecked dimensions

## Summary
Severity: Medium
Advisory: GHSA-cxmj-83gh-fp49
CVE: CVE-2026-48515
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-cxmj-83gh-fp49
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=0 <2.5.301
- NuGet: `MessagePack` — affected >=3.0 <3.1.7

## Details
## Summary

MessagePack-CSharp's multi-dimensional array formatters read dimension lengths directly from the payload and allocate `T[,]`, `T[,,]`, or `T[,,,]` before validating that the dimension product matches the encoded element count.

The formatter reads a guarded element array header, but allocation of the target multi-dimensional array happens before the dimensions are checked against that element count. A small payload can therefore declare large dimensions, provide an empty or tiny inner array, and cause a large heap allocation before element data is validated.

## Impact

Applications are affected when they deserialize untrusted MessagePack payloads into models containing multi-dimensional arrays such as `T[,]`, `T[,,]`, or `T[,,,]`.

An attacker can encode large dimension integers and a small guarded element array. The formatter allocates the target array from the dimensions before confirming that the product of dimensions is consistent with the element count.

The result can be out-of-memory exceptions, container termination on memory-constrained hosts, large object heap pressure, or severe CPU cost from zero-initializing oversized arrays. `MessagePackSecurity.UntrustedData` does not provide a general allocation cap for this path.

## Affected components

- Package: `MessagePack`
- APIs: `TwoDimensionalArrayFormatter<T>.Deserialize`, `ThreeDimensionalArrayFormatter<T>.Deserialize`, `FourDimensionalArrayFormatter<T>.Deserialize`
- Data shapes: `T[,]`, `T[,,]`, and `T[,,,]`
- Finding IDs: `MESSAGEPACKCSHARP-040`, duplicate/open variant `MESSAGEPACKCSHARP-OPEN-003`

## Patches

Fixes are prepared and will be released in coordinated patch versions.

Upgrade guidance:

1. Upgrade `MessagePack` to the patched version for your release line.
2. Upgrade companion MessagePack packages in the same dependency graph to the coordinated patched versions.

The fix should validate dimensions before allocation. Dimension values should be non-negative, their checked product should match the encoded element count, and the product should be bounded by the available payload and any configured security limits before `new T[...]` is executed.

## Workarounds

Patching is recommended.

Until a patched version is available, avoid deserializing untrusted payloads into schemas containing multi-dimensional arrays. Prefer schema shapes that can be validated before allocation, such as bounded lists, dictionaries with application-level count limits, or jagged arrays with application-level limits.

Message-size limits reduce the blast radius but do not fully address allocation amplification where a small payload can encode disproportionate array dimensions.

## Resources

- `MESSAGEPACKCSHARP-040`: unchecked multi-dimensional array dimensions
- `MESSAGEPACKCSHARP-OPEN-003`: duplicate/open finding for the multi-dimensional array issue
- CWE-770: Allocation of Resources Without Limits or Throttling

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-cxmj-83gh-fp49
- https://nvd.nist.gov/vuln/detail/CVE-2026-48515
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
