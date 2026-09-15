# [M] Directory traversal in Mort Bay Jetty

## Summary
Severity: Medium
Advisory: GHSA-9986-w5h5-vw59
CVE: CVE-2009-1523
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-9986-w5h5-vw59
Type: github-advisory

## Affected
- Maven: `org.mortbay.jetty:jetty` — affected >=0 <6.1.17
- Maven: `org.mortbay.jetty:jetty` — affected >=7.0.0.M0 <7.0.0.M2

## Details
Directory traversal vulnerability in the HTTP server in Mort Bay Jetty 5.1.14, 6.x before 6.1.17, and 7.x through 7.0.0.M2 allows remote attackers to access arbitrary files via directory traversal sequences in the URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-1523
- https://bugzilla.redhat.com/show_bug.cgi?id=499867
- https://www.redhat.com/archives/fedora-package-announce/2009-May/msg01257.html
- https://www.redhat.com/archives/fedora-package-announce/2009-May/msg01259.html
- https://www.redhat.com/archives/fedora-package-announce/2009-May/msg01262.html
- http://itrc.hp.com/service/cki/docDisplay.do?docId=emr_na-c02282388
- http://jira.codehaus.org/browse/JETTY-1004
- http://www.kb.cert.org/vuls/id/402580
- http://www.kb.cert.org/vuls/id/CRDY-7RKQCY
- http://www.oracle.com/technetwork/topics/security/cpujul2009-091332.html
- http://www.securityfocus.com/bid/34800
- http://www.securityfocus.com/bid/35675
- http://www.securitytracker.com/id?1022563
- http://www.vupen.com/english/advisories/2009/1900
- http://www.vupen.com/english/advisories/2010/1792
