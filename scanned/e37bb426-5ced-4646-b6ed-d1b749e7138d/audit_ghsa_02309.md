# [C] Missing Authorization in FastReport

## Summary
Severity: Critical
Advisory: GHSA-v726-3vg9-cp34
CVE: CVE-2020-27998
CWE: CWE-862
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-v726-3vg9-cp34
Type: github-advisory

## Affected
- NuGet: `FastReport.OpenSource` — affected >=0 <2020.4.0

## Details
An issue was discovered in FastReport before 2020.4.0. It lacks a ScriptSecurity feature and therefore may mishandle (for example) GetType, typeof, TypeOf, DllImport, LoadLibrary, and GetProcAddress.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27998
- https://github.com/FastReports/FastReport/pull/206
- https://github.com/FastReports/FastReport/compare/v2020.3.0...v2020.4.0
- https://opensource.fast-report.com/2020/09/report-script-security.html
- https://securitylab.github.com/advisories/GHSL-2020-143-FastReportsInc-FastReports
