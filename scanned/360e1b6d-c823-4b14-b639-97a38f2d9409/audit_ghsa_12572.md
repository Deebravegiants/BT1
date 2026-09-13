# [H] YARP Denial of Service Vulnerability

## Summary
Severity: High
Advisory: GHSA-jrjw-qgr2-wfcg
CVE: CVE-2023-33141
CWE: CWE-400
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-23
Source: https://github.com/advisories/GHSA-jrjw-qgr2-wfcg
Type: github-advisory

## Affected
- NuGet: `Yarp.ReverseProxy` — affected >=0 <1.1.2
- NuGet: `Yarp.ReverseProxy` — affected >=2.0.0 <2.0.1

## Details
### Impact
A denial of service vulnerability exists in YARP.

### Patches
If you're using YARP 1.x, you should update to NuGet package version [1.1.2](https://www.nuget.org/packages/Yarp.ReverseProxy/1.1.2).
If you're using YARP 2.0.0, you should update to NuGet package version [2.0.1](https://www.nuget.org/packages/Yarp.ReverseProxy/2.0.1).


You can do so by updating the `PackageReference` in your `.csproj` file
```diff
<ItemGroup>
- <PackageReference Include="Yarp.ReverseProxy" Version="2.0.0" />
- <PackageReference Include="Yarp.Telemetry.Consumption" Version="2.0.0" />
+ <PackageReference Include="Yarp.ReverseProxy" Version="2.0.1" />
+ <PackageReference Include="Yarp.Telemetry.Consumption" Version="2.0.1" />
</ItemGroup>
```
or by selecting `2.0.1` in the NuGet UI inside Visual Studio (`Manage NuGet Packages` / `Updates`)

### References

[CVE-2023-33141](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-33141)

## References
- https://github.com/microsoft/reverse-proxy/security/advisories/GHSA-jrjw-qgr2-wfcg
- https://nvd.nist.gov/vuln/detail/CVE-2023-33141
- https://github.com/microsoft/reverse-proxy
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-33141
- https://www.nuget.org/packages/Yarp.ReverseProxy/1.1.2
- https://www.nuget.org/packages/Yarp.ReverseProxy/2.0.1
