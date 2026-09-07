# [M] Exposure of Sensitive Information to an Unauthorized Actor in JGroup

## Summary
Severity: Medium
Advisory: GHSA-cc62-496p-hrr7
CVE: CVE-2013-4112
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-cc62-496p-hrr7
Type: github-advisory

## Affected
- Maven: `org.jgroups:jgroups` — affected >=3.0.0 <3.2.9.Final
- Maven: `org.jgroups:jgroups` — affected >=3.3.0 <3.3.3.Final

## Details
The DiagnosticsHandler in JGroup 3.0.x, 3.1.x, 3.2.x before 3.2.9, and 3.3.x before 3.3.3 allows remote attackers to obtain sensitive information (diagnostic information) and execute arbitrary code by reusing valid credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4112
- https://bugzilla.redhat.com/show_bug.cgi?id=983489
- http://rhn.redhat.com/errata/RHSA-2013-1207.html
- http://rhn.redhat.com/errata/RHSA-2013-1208.html
- http://rhn.redhat.com/errata/RHSA-2013-1209.html
- http://rhn.redhat.com/errata/RHSA-2013-1437.html
- http://rhn.redhat.com/errata/RHSA-2013-1771.html
- http://rhn.redhat.com/errata/RHSA-2014-0029.html
