# [H] Dom4j contains a XML Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-6pcc-3rfx-4gpm
CVE: CVE-2018-1000632
CWE: CWE-91
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-6pcc-3rfx-4gpm
Type: github-advisory

## Affected
- Maven: `org.dom4j:dom4j` — affected >=0 <2.0.3
- Maven: `org.dom4j:dom4j` — affected >=2.1.0 <2.1.1
- Maven: `dom4j:dom4j` — affected >=0

## Details
dom4j version prior to version 2.1.1 contains a CWE-91: XML Injection vulnerability in Class: Element. Methods: addElement, addAttribute that can result in an attacker tampering with XML documents through XML injection. This attack appear to be exploitable via an attacker specifying attributes or elements in the XML document. This vulnerability appears to have been fixed in 2.1.1 or later.

Note: This advisory applies to `dom4j:dom4j` version 1.x legacy artifacts.  To resolve this a change to the latest version of `org.dom4j:dom4j` is recommended.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000632
- https://github.com/dom4j/dom4j/issues/48
- https://github.com/dom4j/dom4j/commit/e598eb43d418744c4dbf62f647dd2381c9ce9387
- https://github.com/dom4j/dom4j/commit/c2a99d7dee8ce7a4e5bef134bb781a6672bd8a0f
- https://lists.apache.org/thread.html/708d94141126eac03011144a971a6411fcac16d9c248d1d535a39451@%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/7e9e78f0e4288fac6591992836d2a80d4df19161e54bd71ab4b8e458@%3Cdev.maven.apache.org%3E
- https://lists.apache.org/thread.html/7f6e120e6ed473f4e00dde4c398fc6698eb383bd7857d20513e989ce@%3Cdev.maven.apache.org%3E
- https://lists.apache.org/thread.html/9d4c1af6f702c3d6d6f229de57112ddccac8ce44446a01b7937ab9e0@%3Ccommits.maven.apache.org%3E
- https://lists.apache.org/thread.html/d7d960b2778e35ec9b4d40c8efd468c7ce7163bcf6489b633491c89f@%3Cdev.maven.apache.org%3E
- https://lists.apache.org/thread.html/rb1b990d7920ae0d50da5109b73b92bab736d46c9788dd4b135cb1a51@%3Cnotifications.freemarker.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2018/09/msg00028.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IOOVVCRQE6ATFD2JM2EMDXOQXTRIVZGP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KJULAHVR3I5SX7OSMXAG75IMNSAYOXGA
- https://security.netapp.com/advisory/ntap-20190530-0001
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://lists.apache.org/thread.html/5a020ecaa3c701f408f612f7ba2ee37a021644c4a39da2079ed3ddbc@%3Ccommits.maven.apache.org%3E
- https://lists.apache.org/thread.html/4a77652531d62299a30815cf5f233af183425db8e3c9a824a814e768@%3Cdev.maven.apache.org%3E
