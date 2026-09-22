# [H] Infinite loop in .Net Bond

## Summary
Severity: High
Advisory: GHSA-rqrc-8q8f-cp9c
CVE: CVE-2020-1469
CWE: CWE-434, CWE-835
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-08
Source: https://github.com/advisories/GHSA-rqrc-8q8f-cp9c
Type: github-advisory

## Affected
- NuGet: `Bond.Core.CSharp` — affected >=3.0.0 <9.0.1

## Details
A denial of service vulnerability exists when the .NET implementation of Bond improperly parses input, aka 'Bond Denial of Service Vulnerability'. Handling of large container lengths that could cause an infinite loop when deserializing some payloads.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1469
- https://github.com/microsoft/bond/commit/3afea822c42dd0095fedb9e7db9ebb99165e7343
- https://github.com/microsoft/bond/commit/b0fd4a15a7cae946dd2855122559ca59cc34dbea
- https://github.com/microsoft/bond
- https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2020-1469
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1469
- https://www.nuget.org/packages/Bond.Core.CSharp/9.0.1
