# [H] ZK Framework vulnerable to malicious POST

## Summary
Severity: High
Advisory: GHSA-6278-2q4m-cmf3
CVE: CVE-2022-36537
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N/E:H (CVSS_V3)
Published: 2022-08-27
Source: https://github.com/advisories/GHSA-6278-2q4m-cmf3
Type: github-advisory

## Affected
- Maven: `org.zkoss.zk:zk` — affected >=0 <8.6.4.2
- Maven: `org.zkoss.zk:zk` — affected >=9.0.0.0 <9.0.1.3
- Maven: `org.zkoss.zk:zk` — affected >=9.5.0.0 <9.5.1.4
- Maven: `org.zkoss.zk:zk` — affected >=9.6.0.0 <9.6.0.2
- Maven: `org.zkoss.zk:zk` — affected >=9.6.1 <9.6.2

## Details
ZK Framework version 9.6.1, 9.6.0.1, 9.5.1.3, 9.0.1.2 and 8.6.4.1 allows attackers to access sensitive information via a crafted POST request sent to the component AuUploader.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36537
- https://github.com/zkoss/zk/commit/92a29aa9b1daf1fd2d9d188cb6545f0441d54e84
- https://github.com/zkoss/zk
- https://tracker.zkoss.org/browse/ZK-5150
- https://www.bleepingcomputer.com/news/security/cisa-warns-of-hackers-exploiting-zk-java-framework-rce-flaw
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-36537
