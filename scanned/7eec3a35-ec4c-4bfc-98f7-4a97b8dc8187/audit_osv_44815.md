# [H] Workload identity attestation generated before login host validation in Snowflake drivers

## Summary
Severity: High
Advisory: CVE-2026-86600
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86600
Type: osv

## Details
In affected Snowflake drivers, WORKLOAD_IDENTITY authentication requests a cloud workload-identity token and attaches it to the login request without verifying that the configured host is a Snowflake endpoint. An attacker who can modify the connection configuration can cause the driver to mint a fresh attestation and send it to a host they control. The captured token can be replayed to Snowflake for its remaining lifetime in accounts where that workload identity is already registered. On Azure, the token audience is also taken from connection configuration. Combined with an attacker-controlled host, the driver can request a Managed Identity access token scoped to a non-Snowflake Azure resource and deliver it to the attacker. That path is the only case in which impact extends beyond Snowflake; it is bounded by the token lifetime and the managed identity’s permissions. Successful exploitation requires WORKLOAD_IDENTITY authentication on a workload that already has an ambient cloud identity. Patched driver versions restrict this authenticator to recognized Snowflake hosts. Users must manually upgrade.

## References
- https://docs.snowflake.com/en/release-notes/clients-drivers/dotnet-2026#version-610-september-3-2026
- https://docs.snowflake.com/en/release-notes/clients-drivers/golang-2026#version-220-sep-03-2026
- https://docs.snowflake.com/en/release-notes/clients-drivers/jdbc-2026#version-434-sep-03-2026
- https://docs.snowflake.com/en/release-notes/clients-drivers/nodejs-2026#version-330-september-3-2026
- https://docs.snowflake.com/en/release-notes/clients-drivers/odbc-2026#version-3200-sep-3-2026
- https://docs.snowflake.com/en/release-notes/clients-drivers/php-pdo-2026#version-420-sep-3-2026
- https://github.com/snowflakedb/libsnowflakeclient/releases/tag/v2.10.0
- https://github.com/snowflakedb/snowflake-connector-python/releases/tag/v4.7.3
- https://pkg.go.dev
- https://pypi.org
- https://registry.npmjs.org
- https://repo.maven.apache.org/maven2
- https://www.nuget.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86600.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86600
- https://github.com/snowflakedb/gosnowflake
- https://github.com/snowflakedb/libsnowflakeclient
- https://github.com/snowflakedb/pdo_snowflake
- https://github.com/snowflakedb/snowflake-connector-net
- https://github.com/snowflakedb/snowflake-connector-nodejs
