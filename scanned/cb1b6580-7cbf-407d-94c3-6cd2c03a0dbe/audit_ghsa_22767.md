# [M] JBoss RichFaces Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xfxv-f945-4qv6
CVE: CVE-2014-0086
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xfxv-f945-4qv6
Type: github-advisory

## Affected
- Maven: `org.richfaces:richfaces` — affected >=4.3.4
- Maven: `org.richfaces:richfaces` — affected >=5.0.0.Alpha1 <5.0.0.Alpha3

## Details
The doFilter function in webapp/PushHandlerFilter.java in JBoss RichFaces 4.3.4, 4.3.5, and 5.x allows remote attackers to cause a denial of service (memory consumption and out-of-memory error) via a large number of malformed atmosphere push requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0086
- https://github.com/pslegr/core-1/commit/8131f15003f5bec73d475d2b724472e4b87d0757
- https://github.com/richfaces/richfaces/commit/807bc411fba070f78c5193cc03d54ab8aa39c36d
- https://bugzilla.redhat.com/show_bug.cgi?id=1067268
- https://github.com/richfaces/richfaces
- https://issues.jboss.org/browse/RF-13250
- http://rhn.redhat.com/errata/RHSA-2014-0335.html
