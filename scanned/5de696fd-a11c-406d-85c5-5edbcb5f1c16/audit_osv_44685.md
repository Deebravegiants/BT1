# [H] Improper OCSP response validation in Snowflake drivers

## Summary
Severity: High
Advisory: CVE-2026-85525
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85525
Type: osv

## Details
Improper OCSP response validation in the Snowflake Python, Go, JDBC, and Node.js drivers allowed a revoked TLS certificate to be accepted as valid, because OCSP responses were not reliably bound to the certificate being validated and definitive verification failures were treated as transient. A man-in-the-middle attacker holding a revoked certificate and its private key for a Snowflake or stage hostname could cause the driver to establish a TLS session to the attacker-controlled endpoint anyway, allowing the attacker to read and modify data transmitted within that connection. Successful exploitation requires that on-path position and the corresponding private key, and impact is limited to data carried within the intercepted connection. The fix is available in Snowflake Connector for Python v4.7.3, Snowflake Go Driver v2.2.0, Snowflake JDBC Driver v4.3.4 (including the snowflake-jdbc-fips and snowflake-jdbc-thin), and Snowflake Node.js Driver v3.3.0. Users must manually upgrade.

## References
- https://docs.snowflake.com/en/release-notes/clients-drivers/golang-2026
- https://docs.snowflake.com/en/release-notes/clients-drivers/jdbc-2026
- https://docs.snowflake.com/en/release-notes/clients-drivers/nodejs-2026
- https://github.com/snowflakedb/snowflake-connector-python/releases/tag/v4.7.3
- https://pkg.go.dev
- https://pypi.org
- https://registry.npmjs.org
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85525.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85525
- https://github.com/snowflakedb/gosnowflake
- https://github.com/snowflakedb/snowflake-connector-nodejs
- https://github.com/snowflakedb/snowflake-connector-python
- https://github.com/snowflakedb/snowflake-jdbc
