# [H] Apache Storm it is possible for the owner of a topology to trick the supervisor to launch a worker as a different, non-root, user

## Summary
Severity: High
Advisory: GHSA-x825-rjww-2245
CVE: CVE-2017-9799
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-x825-rjww-2245
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm-core` — affected >=1.1.0 <1.1.1
- Maven: `org.apache.storm:storm-core` — affected >=1.0.0 <1.0.4

## Details
It was found that under some situations and configurations of Apache Storm 1.x before 1.0.4 and 1.1.x before 1.1.1, it is theoretically possible for the owner of a topology to trick the supervisor to launch a worker as a different, non-root, user. In the worst case this could lead to secure credentials of the other user being compromised.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9799
- https://github.com/advisories/GHSA-x825-rjww-2245
- https://lists.apache.org/thread.html/b9125bf507ed6f2ca6e85ba1a4b44e232aa70eeddfba2a9d8a954127@%3Cdev.storm.apache.org%3E
- http://www.securityfocus.com/bid/100235
- http://www.securitytracker.com/id/1039116
