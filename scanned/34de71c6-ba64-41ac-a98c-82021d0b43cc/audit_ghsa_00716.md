# [H] XML External Entity Injection in XStream

## Summary
Severity: High
Advisory: GHSA-rgh3-987h-wpmw
CVE: CVE-2016-3674
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-06-30
Source: https://github.com/advisories/GHSA-rgh3-987h-wpmw
Type: github-advisory

## Affected
- Maven: `com.thoughtworks.xstream:xstream` — affected >=0 <1.4.9

## Details
Multiple XML external entity (XXE) vulnerabilities in the (1) Dom4JDriver, (2) DomDriver, (3) JDomDriver, (4) JDom2Driver, (5) SjsxpDriver, (6) StandardStaxDriver, and (7) WstxDriver drivers in XStream before 1.4.9 allow remote attackers to read arbitrary files via a crafted XML document.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3674
- https://github.com/x-stream/xstream/issues/25
- https://github.com/x-stream/xstream
- https://snyk.io/vuln/SNYK-JAVA-COMTHOUGHTWORKSXSTREAM-30385
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183180.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183208.html
- http://rhn.redhat.com/errata/RHSA-2016-2822.html
- http://rhn.redhat.com/errata/RHSA-2016-2823.html
- http://www.debian.org/security/2016/dsa-3575
- http://www.openwall.com/lists/oss-security/2016/03/25/8
- http://www.openwall.com/lists/oss-security/2016/03/28/1
- http://www.securityfocus.com/bid/85381
- http://www.securitytracker.com/id/1036419
- http://x-stream.github.io/changes.html#1.4.9
