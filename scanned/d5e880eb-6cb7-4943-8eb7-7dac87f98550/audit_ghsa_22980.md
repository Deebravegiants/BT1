# [M] Cross site scripting attack in ServiceStack Framework

## Summary
Severity: Medium
Advisory: GHSA-vcfc-9wcp-j623
CVE: CVE-2019-1010199
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vcfc-9wcp-j623
Type: github-advisory

## Affected
- NuGet: `ServiceStack` — affected >=4.5.14 <5.2.0

## Details
ServiceStack ServiceStack Framework 4.5.14 is affected by: Cross Site Scripting (XSS). The impact is: JavaScrpit is reflected in the server response, hence executed by the browser. The component is: the query used in the GET request is prone. The attack vector is: Since there is no server-side validation and If Browser encoding is bypassed, the victim is affected when opening a crafted URL. The fixed version is: 5.2.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010199
- https://github.com/ServiceStack/ServiceStack/commit/a0e0d7de20f5d1712f1793f925496def4383c610
- https://github.com/ServiceStack/ServiceStack
