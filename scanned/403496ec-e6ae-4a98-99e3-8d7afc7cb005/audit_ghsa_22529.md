# [M] Cross-site Scripting in Apache Struts

## Summary
Severity: Medium
Advisory: GHSA-m3x6-9v6h-4g28
CVE: CVE-2016-4003
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-m3x6-9v6h-4g28
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0 <2.3.28

## Details
Cross-site scripting (XSS) vulnerability in the URLDecoder function in JRE before 1.8, as used in Apache Struts 2.x before 2.3.28, when using a single byte page encoding, allows remote attackers to inject arbitrary web script or HTML via multi-byte characters in a url-encoded parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4003
- https://github.com/apache/struts/commit/4720f46a63caaf9db97ba27dc51ac5ad21e66bdc
- https://github.com/apache/struts/commit/5421930b49822606792f36653b17d3d95ef106f9
- https://github.com/apache/struts/commit/72471d7075681bea52046645ad7aa34e9c53751e
- https://github.com/apache/struts/commit/76f188406eb9f17a06afcb5f49f0c44d749da0d2
- https://github.com/apache/struts/commit/a89bbe22cd2461748d595a89a254de888a415e6c
- https://github.com/apache/struts
- https://issues.apache.org/jira/browse/WW-4507
- https://web.archive.org/web/20161119142317/http://www.securityfocus.com/bid/86311
- https://web.archive.org/web/20161221184936/http://www.securitytracker.com/id/1035268
- http://struts.apache.org/docs/s2-028.html
