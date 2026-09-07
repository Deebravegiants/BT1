# [H] Improper Authentication In Apache NiFi

## Summary
Severity: High
Advisory: GHSA-jgj9-6v78-6g8m
CVE: CVE-2017-5635
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jgj9-6v78-6g8m
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=0 <0.7.2
- Maven: `org.apache.nifi:nifi` — affected >=1.0.0 <1.1.2

## Details
In Apache NiFi before 0.7.2 and 1.x before 1.1.2 in a cluster environment, if an anonymous user request is replicated to another node, the originating node identity is used rather than the "anonymous" user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5635
- https://nifi.apache.org/security.html#CVE-2017-5635
- http://www.securityfocus.com/bid/96730
