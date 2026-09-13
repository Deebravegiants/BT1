# [M] User confusion in IronJacamar

## Summary
Severity: Medium
Advisory: GHSA-ppg2-ww3w-hq84
CVE: CVE-2012-3428
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-ppg2-ww3w-hq84
Type: github-advisory

## Affected
- Maven: `org.jboss.ironjacamar:ironjacamar-jdbc` — affected >=0 <1.0.12.Final

## Details
The IronJacamar container before 1.0.12.Final for JBoss Application Server, when allow-multiple-users is enabled in conjunction with a security domain, does not use the credentials supplied in a getConnection function call, which allows remote attackers to obtain access to an arbitrary datasource connection in opportunistic circumstances via an invalid connection attempt.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3428
- https://bugzilla.redhat.com/show_bug.cgi?id=843358
- https://issues.jboss.org/browse/JBJCA-864
- https://issues.jboss.org/browse/JBPAPP-9584
- https://issues.jboss.org/secure/ReleaseNote.jspa?projectId=12310691&version=12319522
- http://rhn.redhat.com/errata/RHSA-2012-1591.html
- http://rhn.redhat.com/errata/RHSA-2012-1592.html
- http://rhn.redhat.com/errata/RHSA-2012-1594.html
- http://secunia.com/advisories/51607
