# [M] Apache XML Security For Java vulnerable to Infinite Loop

## Summary
Severity: Medium
Advisory: GHSA-8gwc-x7mg-7p7p
CVE: CVE-2013-5823
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-8gwc-x7mg-7p7p
Type: github-advisory

## Affected
- Maven: `org.apache.santuario:xmlsec` — affected >=1.4.0 <1.4.8
- Maven: `org.apache.santuario:xmlsec` — affected >=1.5.0 <1.5.3

## Details
Affected versions of xmlsec are subject to a denial of service vulnerability. Should a user check the signature of a message larger than 512 MB, the method `expandSize(int newPos)` of class `org.apache.xml.security.utils.UnsyncByteArrayOutputStream` goes in an endless loop. A remote attacker could use this flaw to supply crafted XML that would lead to a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-5823
- https://github.com/apache/santuario-java/commit/55a48497dfbf3fe63a81e67c13160b3f41ebb1f3
- https://github.com/apache/santuario-java/commit/cea3c91106fb8be35e2f1bb3f1fe0cfddd0ec710
- https://github.com/apache/santuario-java/commit/f9a61f2df9473237aa71308c28113540b4063d33
- https://access.redhat.com/errata/RHSA-2014:0414
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2013-5823
- https://issues.apache.org/jira/browse/SANTUARIO-334
- https://lists.opensuse.org/opensuse-updates/2013-11/msg00023.html
- https://marc.info/?l=bugtraq&m=138674031212883&w=2
- https://marc.info/?l=bugtraq&m=138674073720143&w=2
- https://security.gentoo.org/glsa/glsa-201406-32.xml
