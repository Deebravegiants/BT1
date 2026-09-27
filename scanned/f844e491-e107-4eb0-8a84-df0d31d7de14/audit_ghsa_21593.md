# [C] Apache Jena vulnerable to Deserialization of Untrusted Data

## Summary
Severity: Critical
Advisory: GHSA-g2qw-6vrr-v6pq
CVE: CVE-2022-45136
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-14
Source: https://github.com/advisories/GHSA-g2qw-6vrr-v6pq
Type: github-advisory

## Affected
- Maven: `org.apache.jena:jena-sdb` — affected >=0

## Details
Apache Jena SDB 3.17.0 and earlier is vulnerable to a JDBC Deserialisation attack if the attacker is able to control the JDBC URL used or cause the underlying database server to return malicious data. The mySQL JDBC driver in particular is known to be vulnerable to this class of attack. As a result an application using Apache Jena SDB can be subject to RCE when connected to a malicious database server. Apache Jena SDB has been EOL since December 2020 and users should migrate to alternative options e.g. Apache Jena TDB 2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45136
- https://github.com/apache/jena
- https://lists.apache.org/thread/mc77cdl5stgjtjoldk467gdf756qjt31
- http://www.openwall.com/lists/oss-security/2022/11/14/5
