# [C] Apache Hive: SSRF vulnerability in Hive Avro Serde due to Insufficient input validation on avro.schema.url

## Summary
Severity: Critical
Advisory: CVE-2026-55976
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-55976
Type: osv

## Details
Server-Side Request Forgery (SSRF) in Avro SerDe schema resolution in Apache Hive before 4.2.1 allows an authenticated remote attacker with CREATE TABLE privilege to cause the Hive server to fetch an attacker-controlled URL when resolving the avro.schema.url table property on an Avro table that is subsequently queried. This can expose cloud instance metadata, internal network services, or local server files to the Hive process identity. Users are recommended to upgrade to version 4.2.1, which fixes this issue.



Attacker access requirements:

  *  Network access to HiveServer2 / Metastore: required (remote attacker model).
  *  Valid Hive authentication: required.
  *  CREATE TABLE (or equivalent) privilege: required, so the attacker can set avro.schema.url in table properties.
  *  SELECT privilege on the malicious table: not required for the creator, who can typically query their own table; any other user granted SELECT can also trigger the fetch.
  *  Write access to the table LOCATION: not required; the attack uses the schema URL, not the data path.
  *  Admin / superuser privileges: not required; an ordinary authenticated user with DDL rights is sufficient.
  *  External tables enabled: typically required in practice, and enabled by default in most deployments.




Detection guidance:

  *  Inspect metastore / Hive table metadata for Avro tables whose avro.schema.url uses unexpected schemes such as http, https, file, or ftp, or points at link-local / cloud metadata addresses (for example 169.254.169.254) or other internal hosts.
  *  Review HiveServer2 and Metastore logs around CREATE/ALTER TABLE and queries against Avro tables for schema-resolution failures or outbound fetches of avro.schema.url.
  *  Correlate CREATE TABLE / ALTER TABLE activity that sets avro.schema.url with subsequent SELECT activity on the same table, especially when the URL target is unusual for schema distribution.
  *  On cloud deployments, check instance / VPC flow logs and metadata service access logs for unexpected requests from Hive host identities shortly after Avro DDL or query activity.

## References
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55976.json
- https://lists.apache.org/thread/6d56mk501fp4f8cb5wvrpj2jwd9knt05
- https://nvd.nist.gov/vuln/detail/CVE-2026-55976
- https://issues.apache.org/jira/browse/HIVE-29671
- https://github.com/apache/hive/commit/45049202df35cea382616624de3fe8d252aa2d00
- https://github.com/apache/hive
