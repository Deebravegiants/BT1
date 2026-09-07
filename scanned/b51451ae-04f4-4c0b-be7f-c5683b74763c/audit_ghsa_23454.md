# [H] Apache Brooklyn is vulnerable to cross-site request forgery (CSRF)

## Summary
Severity: High
Advisory: GHSA-g2hf-g7fh-vg92
CVE: CVE-2016-8737
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-g2hf-g7fh-vg92
Type: github-advisory

## Affected
- Maven: `org.apache.brooklyn:brooklyn-rest-resources` — affected >=0 <0.10.0
- Maven: `org.apache.brooklyn:brooklyn-jsgui` — affected >=0 <0.10.0

## Details
In Apache Brooklyn before 0.10.0, the REST server is vulnerable to cross-site request forgery (CSRF), which could permit a malicious web site to produce a link which, if clicked whilst a user is logged in to Brooklyn, would cause the server to execute the attacker's commands as the user. There is known to be a proof-of-concept exploit using this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8737
- https://github.com/apache/brooklyn-server/pull/430
- https://github.com/apache/brooklyn-ui/pull/37
- https://brooklyn.apache.org/community/security/CVE-2016-8737.html
- https://lists.apache.org/thread.html/877813aaaa0e636adbc36106b89a54e0e6918f0884e9c8b67d5d5953%40%3Cdev.brooklyn.apache.org%3E
