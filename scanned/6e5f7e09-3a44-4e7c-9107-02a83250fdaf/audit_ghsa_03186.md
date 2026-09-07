# [C] Insecure deserialization in Wire

## Summary
Severity: Critical
Advisory: GHSA-hpw7-3vq3-mmv6
CVE: CVE-2021-29508
CWE: CWE-502
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-05-19
Source: https://github.com/advisories/GHSA-hpw7-3vq3-mmv6
Type: github-advisory

## Affected
- NuGet: `Wire` — affected >=0

## Details
Due to how Wire handles type information in its serialization format, malicious payloads can be passed to a deserializer. e.g. using a surrogate on the sender end, an attacker can pass information about a different type for the receiving end. And by doing so allowing the serializer to create any type on the deserializing end.

**This is the same issue that exists for .NET BinaryFormatter https://docs.microsoft.com/en-us/visualstudio/code-quality/ca2300?view=vs-2019**

This also applies to the fork of Wire, AkkaDotNet/Hyperion.

## References
- https://github.com/AsynkronIT/Wire/security/advisories/GHSA-hpw7-3vq3-mmv6
- https://nvd.nist.gov/vuln/detail/CVE-2021-29508
- https://www.nuget.org/packages/Wire
