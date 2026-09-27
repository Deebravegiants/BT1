# [H] Csla affected by Remote Code Execution via WcfProxy (NetDataContractSerializer)

## Summary
Severity: High
Advisory: GHSA-wq34-7f4g-953v
CVE: CVE-2025-66631
CWE: CWE-502
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-wq34-7f4g-953v
Type: github-advisory

## Affected
- NuGet: `Csla` — affected >=0 <6.0.0

## Details
### Impact
Versions of CSLA .NET prior to version 6 allow the use of WcfProxy. WcfProxy uses the NetDataContractSerializer (NDCS) which has known vulnerabilities that can allow remote execution of code during deserialization. NDCS itself is considered obsolete, and you should avoid using WcfProxy or upgrade to CSLA 6 or higher where this issue does not exist.

### Patches
CSLA .NET version 6 and higher do not use WCF or NetDataContractSerializer.

### Workarounds
If you are using a version CSLA .NET older than version 6, you should stop using WcfProxy in your data portal configuration. Doing this avoids the use of WCF and the NetDataContractSerializer, avoiding the vulnerability.

## References
- https://github.com/MarimerLLC/csla/security/advisories/GHSA-wq34-7f4g-953v
- https://nvd.nist.gov/vuln/detail/CVE-2025-66631
- https://github.com/MarimerLLC/csla/issues/4001
- https://github.com/MarimerLLC/csla/pull/4018
- https://github.com/MarimerLLC/csla
- https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2310
