# [M] Improper Input Validation in Apache Batik

## Summary
Severity: Medium
Advisory: GHSA-wfw6-mmmp-87xm
CVE: CVE-2015-0250
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wfw6-mmmp-87xm
Type: github-advisory

## Affected
- Maven: `org.apache.xmlgraphics:batik` — affected >=1.0 <1.8

## Details
XML external entity (XXE) vulnerability in the SVG to (1) PNG and (2) JPG conversion classes in Apache Batik 1.x before 1.8 allows remote attackers to read arbitrary files or cause a denial of service via a crafted SVG file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0250
- http://advisories.mageia.org/MGASA-2015-0138.html
- http://packetstormsecurity.com/files/130964/Apache-Batik-XXE-Injection.html
- http://rhn.redhat.com/errata/RHSA-2016-0041.html
- http://rhn.redhat.com/errata/RHSA-2016-0042.html
- http://seclists.org/fulldisclosure/2015/Mar/142
- http://www-01.ibm.com/support/docview.wss?uid=swg21963275
- http://www.debian.org/security/2015/dsa-3205
- http://www.mandriva.com/security/advisories?name=MDVSA-2015:203
- http://www.securitytracker.com/id/1032781
- http://www.ubuntu.com/usn/USN-2548-1
- http://xmlgraphics.apache.org/security.html
