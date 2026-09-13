# [M] Snowflake JDBC Driver auto-configuration account validation permits credential redirection

## Summary
Severity: Medium
Advisory: CVE-2026-85528
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85528
Type: osv

## Details
Improper input validation of the auto-configuration account identifier in Snowflake JDBC Driver versions 4.2.0 through 4.3.3 allowed a credential-bearing login request to be redirected to an attacker-selected HTTPS endpoint. An attacker able to control the account value could cause the driver to transmit a reusable login credential to a host of their choosing and replay it to obtain the privileges granted to that credential. Successful exploitation requires an application using jdbc:snowflake:auto with a connections.toml section that omits an explicit host and a lower-trust principal able to set the account value; ordinary JDBC URLs are unaffected. The fix is available in Snowflake JDBC Driver version 4.3.4, including the snowflake-jdbc-fips and snowflake-jdbc-thin. Users must manually upgrade.

## References
- https://docs.snowflake.com/en/release-notes/clients-drivers/jdbc-2026#version-434-sep-03-2026
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85528.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85528
- https://github.com/snowflakedb/snowflake-jdbc
