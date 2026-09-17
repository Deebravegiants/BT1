# [M] Nerdbank.MessagePack has Inefficient CPU Computation

## Summary
Severity: Medium
Advisory: GHSA-92vj-hp7m-gwcj
CWE: CWE-1176
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-92vj-hp7m-gwcj
Type: github-advisory

## Affected
- NuGet: `Nerdbank.MessagePack` — affected >=0 <1.2.4

## Details
### Impact

Applications that call `OptionalConverters.WithExpandoObjectConverter` and deserialize untrusted data are open to a vulnerability by which an attacker can exploit a `O(n²)` algorithm to burn an inordinate amount of CPU effort by adding a great many properties to an `ExpandoObject`, whose `Add` method is implemented as an `O(n)` algorithm.

### Patches

Update to a patched version.

If a project's `ExpandoObject` data requires more than 128 properties, the default limit should be changed:

```cs
this.Serializer = this.Serializer with
{
	StartingContext = this.Serializer.StartingContext with
	{
		Security = this.Serializer.StartingContext.Security with
		{
			ExpandoObjectMaxPropertyCount = 256, // Set this to whatever limit is required by your application
		},
	},
};
```

### Workarounds

Avoid the non-default `WithExpandoObjectConverter` extension method when deserializing untrusted data.
If deserializing untrusted data into an `ExpandoObject` is required, developers should write a custom converter for their project that limits the number of properties allowed before initializing the object.

## References
- https://github.com/AArnott/Nerdbank.MessagePack/security/advisories/GHSA-92vj-hp7m-gwcj
- https://github.com/AArnott/Nerdbank.MessagePack/commit/c5a239e4f20c38548de44c4dd2a782efd5e2547c
- https://github.com/AArnott/Nerdbank.MessagePack
