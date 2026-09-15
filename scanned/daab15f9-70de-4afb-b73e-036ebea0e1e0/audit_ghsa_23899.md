# [M] Apache MyFaces Vulnerable to Path Traversal

## Summary
Severity: Medium
Advisory: GHSA-gjfx-9wx3-j6r7
CVE: CVE-2011-4367
CWE: CWE-22
Ecosystem: Maven
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gjfx-9wx3-j6r7
Type: github-advisory

## Affected
- Maven: `org.apache.myfaces.core:myfaces-impl` — affected >=2.0.0 <2.0.12
- Maven: `org.apache.myfaces.core:myfaces-impl` — affected >=2.1.0 <2.1.6

## Details
Multiple directory traversal vulnerabilities in MyFaces JavaServer Faces (JSF) in Apache MyFaces Core 2.0.x before 2.0.12 and 2.1.x before 2.1.6 allow remote attackers to read arbitrary files via a `..` (dot dot) in the (1) ln parameter to `faces/javax.faces.resource/web.xml` or (2) the `PATH_INFO` to `faces/javax.faces.resource/`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4367
- https://exchange.xforce.ibmcloud.com/vulnerabilities/73100
- https://web.archive.org/web/20120213042504/http://www.securityfocus.com/bid/51939
- http://mail-archives.apache.org/mod_mbox/myfaces-announce/201202.mbox/%3C4F33ED1F.4070007%40apache.org%3E
- http://seclists.org/fulldisclosure/2012/Feb/150
