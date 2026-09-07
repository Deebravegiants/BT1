# [H] Improper Authentication in hive:hive-exec

## Summary
Severity: High
Advisory: GHSA-rrfq-g5fq-fc9c
CVE: CVE-2018-11777
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-rrfq-g5fq-fc9c
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive-exec` — affected >=3.0.0 <3.1.1
- Maven: `org.apache.hive:hive-exec` — affected >=0 <2.3.4

## Details
In Apache Hive 2.3.3, 3.1.0 and earlier, local resources on HiveServer2 machines are not properly protected against malicious user if ranger, sentry or sql standard authorizer is not in use.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11777
- https://github.com/advisories/GHSA-rrfq-g5fq-fc9c
- https://lists.apache.org/thread.html/963c8e2516405c9b532b4add16c03b2c5db621e0c83e80f45049cbbb@%3Cdev.hive.apache.org%3E
- http://www.securityfocus.com/bid/105886
