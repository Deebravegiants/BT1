# [M] Improper Authentication in Apache Tomcat

## Summary
Severity: Medium
Advisory: GHSA-28cq-6rmx-pjq4
CVE: CVE-2012-5887
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-28cq-6rmx-pjq4
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=5.5.0 <5.5.36
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.36
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.30

## Details
The HTTP Digest Access Authentication implementation in Apache Tomcat 5.5.x before 5.5.36, 6.x before 6.0.36, and 7.x before 7.0.30 does not properly check for stale nonce values in conjunction with enforcement of proper credentials, which makes it easier for remote attackers to bypass intended access restrictions by sniffing the network for valid requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5887
- https://exchange.xforce.ibmcloud.com/vulnerabilities/79809
- https://github.com/apache/tomcat
- http://lists.opensuse.org/opensuse-updates/2012-12/msg00089.html
- http://lists.opensuse.org/opensuse-updates/2012-12/msg00090.html
- http://lists.opensuse.org/opensuse-updates/2013-01/msg00037.html
- http://rhn.redhat.com/errata/RHSA-2013-0623.html
- http://rhn.redhat.com/errata/RHSA-2013-0629.html
- http://rhn.redhat.com/errata/RHSA-2013-0631.html
- http://rhn.redhat.com/errata/RHSA-2013-0632.html
- http://rhn.redhat.com/errata/RHSA-2013-0640.html
- http://rhn.redhat.com/errata/RHSA-2013-0647.html
- http://rhn.redhat.com/errata/RHSA-2013-0648.html
- http://rhn.redhat.com/errata/RHSA-2013-0726.html
- http://svn.apache.org/viewvc?view=revision&revision=1377807
- http://svn.apache.org/viewvc?view=revision&revision=1380829
- http://svn.apache.org/viewvc?view=revision&revision=1392248
- http://tomcat.apache.org/security-5.html
- http://tomcat.apache.org/security-6.html
- http://tomcat.apache.org/security-7.html
