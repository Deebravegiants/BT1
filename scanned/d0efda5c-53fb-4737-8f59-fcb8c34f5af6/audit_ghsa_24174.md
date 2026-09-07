# [M] NuGet Package Manager Tampering Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3hcm-6fjc-47qq
CVE: CVE-2019-0976
CWE: CWE-732
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3hcm-6fjc-47qq
Type: github-advisory

## Affected
- NuGet: `NuGet.Commands` — affected >=5.0.0 <5.0.2

## Details
A tampering vulnerability exists in the NuGet Package Manager for Linux and Mac that could allow an authenticated attacker to modify contents of the intermediate build folder (by default `obj`), aka 'NuGet Package Manager Tampering Vulnerability'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0976
- https://github.com/NuGet/Home/issues/7908
- https://github.com/NuGet/NuGet.Client/commit/e32a2ea7096debd3e513188f6779bb1041593326
- https://github.com/NuGet/NuGet.Client
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0976
- https://web.archive.org/web/20200227075944/http://www.securityfocus.com/bid/108210
