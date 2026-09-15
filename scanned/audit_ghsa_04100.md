# [C] Improper Input Validation in net.sf.robocode:robocode.host allows for external service interaction

## Summary
Severity: Critical
Advisory: GHSA-q2xp-75m7-gv52
CVE: CVE-2019-10648
CWE: CWE-20, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-04-02
Source: https://github.com/advisories/GHSA-q2xp-75m7-gv52
Type: github-advisory

## Affected
- Maven: `net.sf.robocode:robocode.host` — affected >=0 <1.9.3.7

## Details
Robocode through 1.9.3.5 allows remote attackers to cause external service interaction (DNS), as demonstrated by a query for a unique subdomain name within an attacker-controlled DNS zone, because of a .openStream call within java.net.URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10648
- https://github.com/robo-code/robocode/commit/836c84635e982e74f2f2771b2c8640c3a34221bd#diff-0296a8f9d4a509789f4dc4f052d9c36f
- https://sourceforge.net/p/robocode/bugs/406
