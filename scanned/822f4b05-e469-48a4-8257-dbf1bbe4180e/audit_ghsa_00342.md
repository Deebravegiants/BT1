# [H] High severity vulnerability that affects org.apache.tika:tika-core

## Summary
Severity: High
Advisory: GHSA-6jq2-789q-fff2
CVE: CVE-2018-11761
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-6jq2-789q-fff2
Type: github-advisory

## Affected
- Maven: `org.apache.tika:tika-core` — affected >=0.1 <1.19.1

## Details
In Apache Tika 0.1 to 1.18, the XML parsers were not configured to limit entity expansion. They were therefore vulnerable to an entity expansion vulnerability which can lead to a denial of service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11761
- https://github.com/advisories/GHSA-6jq2-789q-fff2
- https://lists.apache.org/thread.html/5553e10bba5604117967466618f219c0cae710075819c70cfb3fb421@%3Cdev.tika.apache.org%3E
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451@%3Csolr-user.lucene.apache.org%3E
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- http://www.securityfocus.com/bid/105514
