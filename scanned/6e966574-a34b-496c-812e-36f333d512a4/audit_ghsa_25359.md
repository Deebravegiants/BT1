# [M] Apache Tomcat Sensitive Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-5x5f-9r6q-q7mh
CVE: CVE-2008-0002
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-5x5f-9r6q-q7mh
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.0 <6.0.16

## Details
Apache Tomcat 6.0.0 through 6.0.15 processes parameters in the context of the wrong request when an exception occurs during parameter processing, which might allow remote attackers to obtain sensitive information, as demonstrated by disconnecting during this processing in order to trigger the exception.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-0002
- https://github.com/apache/tomcat
- https://web.archive.org/web/20080214133036/http://secunia.com/advisories/28915
- https://web.archive.org/web/20080715062302/http://secunia.com/advisories/29711
- https://web.archive.org/web/20080724052339/http://secunia.com/advisories/28834
- https://web.archive.org/web/20081012021650/http://www.securityfocus.com/bid/27703
- https://web.archive.org/web/20081013050642/http://secunia.com/advisories/32222
- https://web.archive.org/web/20081120062646/http://securityreason.com/securityalert/3638
- https://web.archive.org/web/20081121133027/http://www.securityfocus.com/archive/1/487812/100/0/threaded
- https://web.archive.org/web/20091125140215/http://secunia.com/advisories/37460
- https://web.archive.org/web/20120825080137/http://www.securityfocus.com/bid/31681
- https://web.archive.org/web/20140723000733/http://secunia.com/advisories/57126
- https://web.archive.org/web/20150621204350/http://www.securityfocus.com/archive/1/507985/100/0/threaded
- https://www.redhat.com/archives/fedora-package-announce/2008-February/msg00315.html
- https://www.redhat.com/archives/fedora-package-announce/2008-February/msg00460.html
- http://lists.apple.com/archives/security-announce/2008/Oct/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2009-02/msg00002.html
- http://marc.info/?l=bugtraq&m=139344343412337&w=2
- http://security.gentoo.org/glsa/glsa-200804-10.xml
- http://support.apple.com/kb/HT3216
