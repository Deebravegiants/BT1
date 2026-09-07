# [H] Session Fixation in Apache Zeppelin

## Summary
Severity: High
Advisory: GHSA-c538-924g-99q4
CVE: CVE-2017-12619
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2019-04-24
Source: https://github.com/advisories/GHSA-c538-924g-99q4
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:zeppelin` — affected >=0 <0.7.3

## Details
Apache Zeppelin prior to 0.7.3 was vulnerable to session fixation which allowed an attacker to hijack a valid user session. Issue was reported by "stone lone".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12619
- https://lists.apache.org/thread.html/ff6b995a5a3ba8db4d6b14b4d9dd487e7bf2e3bdd5b375b64a25fd06@%3Cusers.zeppelin.apache.org%3E
- https://zeppelin.apache.org/releases/zeppelin-release-0.7.3.html
- http://www.openwall.com/lists/oss-security/2019/04/23/1
