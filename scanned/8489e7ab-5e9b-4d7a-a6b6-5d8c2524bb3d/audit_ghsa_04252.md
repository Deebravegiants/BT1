# [M] MessagePack-CSharp: ASP.NET Core MessagePackInputFormatter defaults to TrustedData for HTTP request bodies

## Summary
Severity: Medium
Advisory: GHSA-2f33-pr97-265q
CVE: CVE-2026-48509
CWE: CWE-1188
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-2f33-pr97-265q
Type: github-advisory

## Affected
- NuGet: `MessagePack` — affected >=0 <2.5.301
- NuGet: `MessagePack` — affected >=3.0 <3.1.7

## Details
## Summary

The parameterless `MessagePackInputFormatter()` constructor uses default serializer options, which resolve to `MessagePackSerializerOptions.Standard` with `MessagePackSecurity.TrustedData`. The formatter is designed for ASP.NET Core MVC request bodies, which commonly cross an HTTP trust boundary.

This insecure default can expose applications to denial-of-service attacks that `MessagePackSecurity.UntrustedData` is intended to mitigate, such as hash-collision attacks against dictionary-like model properties.

## Impact

Applications are affected when they register `new MessagePackInputFormatter()` without explicitly passing serializer options configured for untrusted data.

An unauthenticated or otherwise untrusted HTTP client can send MessagePack request bodies that are deserialized using the trusted-data posture. For models containing hash-based collections, this can enable algorithmic complexity attacks using colliding keys. The default constructor makes the unsafe posture easy to use at the exact boundary where request bodies should be treated as untrusted.

## Affected components

- Package: `MessagePack.AspNetCoreMvcFormatter`
- API: `MessagePackInputFormatter()` parameterless constructor
- Scenario: ASP.NET Core MVC model binding from HTTP request bodies
- Finding IDs: `MESSAGEPACKCSHARP-OPEN-009`, duplicate `MESSAGEPACKCSHARP-095`

## Patches

Fixes are prepared and will be released in coordinated patch versions.

Upgrade guidance:

1. Upgrade `MessagePack.AspNetCoreMvcFormatter` to the patched version for your release line.
2. Upgrade companion MessagePack packages in the same dependency graph to the coordinated patched versions.

The fix should default the parameterless constructor to `MessagePackSerializerOptions.Standard.WithSecurity(MessagePackSecurity.UntrustedData)`, or require callers to pass explicit options so the trust posture is deliberate.

## Workarounds

Do not use the parameterless constructor on affected versions. Register the formatter with explicit untrusted-data options, for example:

```csharp
options.InputFormatters.Add(
    new MessagePackInputFormatter(
        MessagePackSerializerOptions.Standard.WithSecurity(MessagePackSecurity.UntrustedData)));
```

Also apply normal HTTP request-size limits and model validation appropriate for your service.

## Resources

- `MESSAGEPACKCSHARP-OPEN-009`: MVC input formatter defaults to trusted-data security posture
- `MESSAGEPACKCSHARP-095`: duplicate finding for the same root cause
- CWE-1188: Initialization of a Resource with an Insecure Default

## References
- https://github.com/MessagePack-CSharp/MessagePack-CSharp/security/advisories/GHSA-2f33-pr97-265q
- https://nvd.nist.gov/vuln/detail/CVE-2026-48509
- https://github.com/MessagePack-CSharp/MessagePack-CSharp
