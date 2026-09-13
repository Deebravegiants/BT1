# [H] High severity vulnerability that affects YamlDotNet and YamlDotNet.Signed

## Summary
Severity: High
Advisory: GHSA-rpch-cqj9-h65r
CVE: CVE-2018-1000210
CWE: CWE-502, CWE-639
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-rpch-cqj9-h65r
Type: github-advisory

## Affected
- NuGet: `YamlDotNet` — affected >=0 <5.0.0
- NuGet: `YamlDotNet.Signed` — affected >=0 <5.0.0

## Details
YamlDotNet version 4.3.2 and earlier contains a Insecure Direct Object Reference vulnerability in The default behavior of Deserializer.Deserialize() will deserialize user-controlled types in the line "currentType = Type.GetType(nodeEvent.Tag.Substring(1), throwOnError: false);" and blindly instantiates them. that can result in Code execution in the context of the running process. This attack appear to be exploitable via Victim must parse a specially-crafted YAML file. This vulnerability appears to have been fixed in 5.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000210
- https://github.com/aaubry/YamlDotNet#version-500
- https://github.com/aaubry/YamlDotNet/blob/f96b7cc40a0498f8bafdeb49df3aa23aa2c60993/YamlDotNet/Serialization/NodeTypeResolvers/TypeNameInTagNodeTypeResolver.cs#L35
- https://github.com/advisories/GHSA-rpch-cqj9-h65r
- ps://github.com/aaubry/YamlDotNet
