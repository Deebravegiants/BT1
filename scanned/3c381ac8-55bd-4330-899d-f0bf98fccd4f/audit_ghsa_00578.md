# [H] High severity vulnerability that affects org.apache.hive:hive, org.apache.hive:hive-exec, and org.apache.hive:hive-service

## Summary
Severity: High
Advisory: GHSA-83r3-c79w-f6wc
CVE: CVE-2015-7521
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-83r3-c79w-f6wc
Type: github-advisory

## Affected
- Maven: `org.apache.hive:hive` — affected >=1.0.0 <1.2.2
- Maven: `org.apache.hive:hive-exec` — affected >=1.0.0 <1.2.2
- Maven: `org.apache.hive:hive-service` — affected >=1.0.0 <1.2.2

## Details
The authorization framework in Apache Hive 1.0.0, 1.0.1, 1.1.0, 1.1.1, 1.2.0 and 1.2.1, on clusters protected by Ranger and SqlStdHiveAuthorization, allows attackers to bypass intended parent table access restrictions via unspecified partition-level operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7521
- https://github.com/advisories/GHSA-83r3-c79w-f6wc
- http://mail-archives.apache.org/mod_mbox/hive-user/201601.mbox/%3C20160128205008.2154F185EB%40minotaur.apache.org%3E
- http://packetstormsecurity.com/files/135836/Apache-Hive-Authorization-Bypass.html
- http://www.openwall.com/lists/oss-security/2016/01/28/12
- http://www.securityfocus.com/archive/1/537549/100/0/threaded
