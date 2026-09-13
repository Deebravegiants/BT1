# [H] Drools Improper Input Validation vulnerability allows remote attackers to execute arbitrary code in JBoss EAP

## Summary
Severity: High
Advisory: GHSA-qvq6-cw53-rmwg
CVE: CVE-2010-3708
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qvq6-cw53-rmwg
Type: github-advisory

## Affected
- Maven: `org.drools:drools-core` — affected >=0 <4.0.7

## Details
The serialization implementation in JBoss Drools in Red Hat JBoss Enterprise Application Platform (aka JBoss EAP or JBEAP) 4.3 before 4.3.0.CP09 and JBoss Enterprise SOA Platform 4.2 and 4.3 supports the embedding of class files, which allows remote attackers to execute arbitrary code via a crafted static initializer.

The maintainers of JBoss EAP patched the vulnerability by applying a fix from Drools 4.0.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3708
- https://bugzilla.redhat.com/show_bug.cgi?id=633859
- https://issues.jboss.org/browse/SOA-2319
- https://web.archive.org/web/20111025030056/http://securitytracker.com/id?1024813
- http://www.redhat.com/support/errata/RHSA-2010-0937.html
- http://www.redhat.com/support/errata/RHSA-2010-0938.html
- http://www.redhat.com/support/errata/RHSA-2010-0939.html
- http://www.redhat.com/support/errata/RHSA-2010-0940.html
