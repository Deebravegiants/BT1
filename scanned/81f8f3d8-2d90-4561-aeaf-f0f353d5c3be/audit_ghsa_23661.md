# [M] Inefficient Algorithmic Complexity in Apache Santuario XML Security

## Summary
Severity: Medium
Advisory: GHSA-r237-w2w6-jq3p
CVE: CVE-2013-2172
CWE: CWE-407
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r237-w2w6-jq3p
Type: github-advisory

## Affected
- Maven: `org.apache.santuario:xmlsec` — affected >=1.4.0 <1.4.8
- Maven: `org.apache.santuario:xmlsec` — affected >=1.5.0 <1.5.5

## Details
`jcp/xml/dsig/internal/dom/DOMCanonicalizationMethod.java` in Apache Santuario XML Security for Java 1.4.x before 1.4.8 and 1.5.x before 1.5.5 allows context-dependent attackers to spoof an XML Signature by using the CanonicalizationMethod parameter to specify an arbitrary weak "canonicalization algorithm to apply to the SignedInfo part of the Signature."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2172
- https://github.com/apache/santuario-java/commit/25e0e11493b061749f778030036cb5c406b34590
- https://github.com/apache/santuario-java/commit/8e8f8bf92a43608d7d5f9e357fae19244454a61f
- https://github.com/apache/santuario-java
- https://lists.apache.org/thread.html/680e6938b6412e26d5446054fd31de2011d33af11786b989127d1cc3%40%3Ccommits.santuario.apache.org%3E
- https://lists.apache.org/thread.html/680e6938b6412e26d5446054fd31de2011d33af11786b989127d1cc3@%3Ccommits.santuario.apache.org%3E
- https://lists.apache.org/thread.html/r1c07a561426ec5579073046ad7f4207cdcef452bb3100abaf908e0cd%40%3Ccommits.santuario.apache.org%3E
- https://lists.apache.org/thread.html/r1c07a561426ec5579073046ad7f4207cdcef452bb3100abaf908e0cd@%3Ccommits.santuario.apache.org%3E
- https://web.archive.org/web/20160317145515/http://www.securityfocus.com/archive/1/534161/100/0/threaded
- https://web.archive.org/web/20200228060314/http://www.securityfocus.com/bid/60846
- http://rhn.redhat.com/errata/RHSA-2013-1207.html
- http://rhn.redhat.com/errata/RHSA-2013-1208.html
- http://rhn.redhat.com/errata/RHSA-2013-1209.html
- http://rhn.redhat.com/errata/RHSA-2013-1217.html
- http://rhn.redhat.com/errata/RHSA-2013-1218.html
- http://rhn.redhat.com/errata/RHSA-2013-1219.html
- http://rhn.redhat.com/errata/RHSA-2013-1220.html
- http://rhn.redhat.com/errata/RHSA-2013-1375.html
- http://rhn.redhat.com/errata/RHSA-2013-1437.html
- http://rhn.redhat.com/errata/RHSA-2013-1853.html
