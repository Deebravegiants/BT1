# [C] New Relic .NET Agent contains SQL Injection

## Summary
Severity: Critical
Advisory: GHSA-2rvx-cvfc-mcp2
CVE: CVE-2017-9246
CWE: CWE-89
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2rvx-cvfc-mcp2
Type: github-advisory

## Affected
- NuGet: `NewRelic.Agent` — affected >=0 <6.3.123.0

## Details
New Relic .NET Agent before 6.3.123.0 adds SQL injection flaws to safe applications via vectors involving failure to escape quotes during use of the Slow Queries feature, as demonstrated by a mishandled quote in a VALUES clause of an INSERT statement, after bypassing a SET SHOWPLAN_ALL ON protection mechanism.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9246
- https://github.com/newrelic/newrelic-dotnet-agent
- https://web.archive.org/web/20221202191459/https://blog.seanmcelroy.com/2017/05/26/sql-injection-with-new-relic-patched
