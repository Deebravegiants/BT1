# [H] Yauaa vulnerable to ArrayIndexOutOfBoundsException triggered by a crafted Sec-Ch-Ua-Full-Version-List

## Summary
Severity: High
Advisory: GHSA-c4pm-63cg-9j7h
CVE: CVE-2022-23496
CWE: CWE-755
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-08
Source: https://github.com/advisories/GHSA-c4pm-63cg-9j7h
Type: github-advisory

## Affected
- Maven: `nl.basjes.parse.useragent:yauaa` — affected >=7.0.0 <7.9.0
- Maven: `nl.basjes.parse.useragent:yauaa-beam` — affected >=7.0.0 <7.9.0
- Maven: `nl.basjes.parse.useragent:yauaa-beam-sql` — affected >=7.0.0 <7.9.0
- Maven: `nl.basjes.parse.useragent:yauaa-drill` — affected >=7.0.0 <7.9.0
- Maven: `nl.basjes.parse.useragent:yauaa-elasticsearch` — affected >=7.0.0 <7.9.0
- Maven: `nl.basjes.parse.useragent:yauaa-elasticsearch-8` — affected >=7.0.0 <7.9.0
- Maven: `nl.basjes.parse.useragent:yauaa-flink` — affected >=7.0.0 <7.9.0
- Maven: `nl.basjes.parse.useragent:yauaa-flink-table` — affected >=7.0.0 <7.9.0
- Maven: `nl.basjes.parse.useragent:yauaa-hive` — affected >=7.0.0 <7.9.0
- Maven: `nl.basjes.parse.useragent:yauaa-logparser` — affected >=7.0.0 <7.9.0
- Maven: `nl.basjes.parse.useragent:yauaa-snowflake` — affected >=7.0.0 <7.9.0
- Maven: `nl.basjes.parse.useragent:yauaa-trino` — affected >=7.0.0 <7.9.0

## Details
### Impact
Applications using the Client Hints analysis feature introduced with 7.0.0 can crash because the Yauaa library throws an ArrayIndexOutOfBoundsException. Applications that do not use this feature are not affected.

### Patches
Upgrade to 7.9.0

### Workarounds
Catch and discard any exceptions from Yauaa.

## References
- https://github.com/nielsbasjes/yauaa/security/advisories/GHSA-c4pm-63cg-9j7h
- https://nvd.nist.gov/vuln/detail/CVE-2022-23496
- https://github.com/nielsbasjes/yauaa/commit/3017a866e2cff0d308f264b66fde4fa79e3beb9e
- https://github.com/nielsbasjes/yauaa
