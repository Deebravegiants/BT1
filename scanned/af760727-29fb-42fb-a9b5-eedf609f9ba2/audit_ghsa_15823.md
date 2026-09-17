# [M] Snowflake JDBC Security Advisory

## Summary
Severity: Medium
Advisory: GHSA-f686-hw9c-xw9c
CVE: CVE-2024-43382
CWE: CWE-311, CWE-326
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-10-30
Source: https://github.com/advisories/GHSA-f686-hw9c-xw9c
Type: github-advisory

## Affected
- Maven: `net.snowflake:snowflake-jdbc` — affected >=3.2.6 <3.20.0

## Details
### Impacted Products
Snowflake JDBC driver versions >= 3.2.6 & <= 3.19.1 are affected.

### Introduction
Snowflake recently identified an issue affecting JDBC drivers that can result in data being uploaded to an encrypted stage without the additional layer of protection provided by client side encryption. The issue, which affects only a subset of accounts hosted on Azure and GCP deployments (AWS deployments are not affected), manifests in instances where customers create a stage using a JDBC driver with the CLIENT_ENCRYPTION_KEY_SIZE account parameter set to 256-bit rather than the default 128-bit. The data is still protected by TLS in transit and server side encryption at rest. This missed layer of the additional protection is not visible to the affected customers.

### Incorrect Security Setting Vulnerability 
#### Description
Snowflake identified an incorrect security setting in Snowflake JDBC drivers. Snowflake has evaluated the severity of the issue and determined it was in medium range with a maximum CVSSv3 base score of 5.9. 
#### Scenarios and attack vector(s)
Users of Snowflake JDBC drivers with accounts on Azure and GCP deployments who set the parameter CLIENT_ENCRYPTION_KEY_SIZE = 256 were subject to this incorrect security setting vulnerability as it could result in data being uploaded to a stage without an additional layer for encryption. 
#### Our response
On July 23, 2024, Snowflake discovered this vulnerability. On 10/28/2024, Snowflake released a patch in Snowflake JDBC driver Version 3.20.0. The patch fixes the incorrect security setting. 
#### Resolution
We strongly recommend users to upgrade to 3.20.0 or later versions as soon as possible. 

### Contact
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/snowflake-jdbc/security/advisories/GHSA-f686-hw9c-xw9c
- https://nvd.nist.gov/vuln/detail/CVE-2024-43382
- https://github.com/snowflakedb/snowflake-jdbc
