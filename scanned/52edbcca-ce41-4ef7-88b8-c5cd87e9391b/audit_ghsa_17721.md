# [M] Snowflake.Data has weak temporary files permissions

## Summary
Severity: Medium
Advisory: GHSA-2mqw-rq5m-8hc8
CVE: CVE-2025-24788
CWE: CWE-276
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-2mqw-rq5m-8hc8
Type: github-advisory

## Affected
- NuGet: `Snowflake.Data` — affected >=2.0.12 <4.3.0

## Details
### Issue
Snowflake discovered and remediated a vulnerability in the Snowflake Connector for .NET in which files downloaded from stages are temporarily placed in a world-readable local directory, making them accessible to unauthorized users on the same machine.

This vulnerability affects versions 2.0.12 through 4.2.0 on Linux and macOS. Snowflake fixed the issue in version 4.3.0.

### Vulnerability Details
When downloading files from stages, the Snowflake Connector for .NET uses the OS temporary directory to save files before copying them to the destination directory. The files in the temporary directory, which are removed once the write to the destination directory concludes, have world-readable permissions on Linux and macOS. This could allow any user on the local machine to access them during their limited lifetime.

### Solution
Snowflake released version 4.3.0 of the Snowflake Connector for .NET, which fixes this issue. We recommend users upgrade to version 4.3.0.

### Additional Information
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/snowflake-connector-net/security/advisories/GHSA-2mqw-rq5m-8hc8
- https://nvd.nist.gov/vuln/detail/CVE-2025-24788
- https://github.com/snowflakedb/snowflake-connector-net/commit/89d91e8316ca213c5d184bcf469ed93977a5edf9
- https://github.com/snowflakedb/snowflake-connector-net
