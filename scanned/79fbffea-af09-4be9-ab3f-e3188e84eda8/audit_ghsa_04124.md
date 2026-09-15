# [H] org.apache.hive:hive, org.apache.hive:hive-exec, and org.apache.hive:hive-service vulnerable to Improper Certificate Validation 

## Summary
Severity: High
Advisory: GHSA-gf2v-9hp6-44qg
CVE: CVE-2016-3083
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-03-14
Source: https://github.com/advisories/GHSA-gf2v-9hp6-44qg
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive` — affected >=0 <1.2.2
- Maven: `org.apache.hive:hive` — affected >=2.0.0 <2.0.1
- Maven: `org.apache.hive:hive-service` — affected >=0 <1.2.2
- Maven: `org.apache.hive:hive-service` — affected >=2.0.0 <2.0.1
- Maven: `org.apache.hive:hive-exec` — affected >=0 <1.2.2
- Maven: `org.apache.hive:hive-exec` — affected >=2.0.0 <2.0.1

## Details
Apache Hive (JDBC + HiveServer2) implements SSL for plain TCP and HTTP connections (it supports both transport modes). While validating the server's certificate during the connection setup, the client in Apache Hive before 1.2.2 and 2.0.x before 2.0.1 doesn't seem to be verifying the common name attribute of the certificate. In this way, if a JDBC client sends an SSL request to server abc.com, and the server responds with a valid certificate (certified by CA) but issued to xyz.com, the client will accept that as a valid certificate and the SSL handshake will go through.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3083
- https://github.com/advisories/GHSA-gf2v-9hp6-44qg
- https://lists.apache.org/thread.html/0851bcf85635385f94cdaa008053802d92b4aab0a3075e30ed171192@%3Cdev.hive.apache.org%3E
- http://www.securityfocus.com/bid/98669
