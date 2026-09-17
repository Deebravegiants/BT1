# [C] QuantConnect Lean vulnerable to insecure deserialization

## Summary
Severity: Critical
Advisory: GHSA-ww7r-278h-48mh
CVE: CVE-2020-20136
CWE: CWE-502
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-ww7r-278h-48mh
Type: github-advisory

## Affected
- NuGet: `QuantConnect.Common` — affected >=2.3.0.0

## Details
QuantConnect Lean versions from 2.3.0.0 to 2.4.0.1 are affected by an insecure deserialization vulnerability due to insecure configuration of TypeNameHandling property in Json.NET library. One may avoid this issue by only running Lean in an environment where data provided is trusted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-20136
- https://github.com/QuantConnect/Lean/issues/3537
- https://github.com/QuantConnect/Lean
