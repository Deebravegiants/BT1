# [C] Injection in Apache NiFi

## Summary
Severity: Critical
Advisory: GHSA-jrcc-7jf5-3pxg
CVE: CVE-2017-5636
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jrcc-7jf5-3pxg
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=0 <0.7.2
- Maven: `org.apache.nifi:nifi` — affected >=1.0.0 <1.1.2

## Details
In Apache NiFi before 0.7.2 and 1.x before 1.1.2 in a cluster environment, the proxy chain serialization/deserialization is vulnerable to an injection attack where a carefully crafted username could impersonate another user and gain their permissions on a replicated request to another node.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5636
- https://nifi.apache.org/security.html#CVE-2017-5636
- http://www.securityfocus.com/bid/96731
