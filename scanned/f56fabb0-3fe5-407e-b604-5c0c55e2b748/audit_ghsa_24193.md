# [H] Apache Struts forced double OGNL evaluation

## Summary
Severity: High
Advisory: GHSA-864w-r5qj-h6fj
CVE: CVE-2016-4461
CWE: CWE-20, CWE-74
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-864w-r5qj-h6fj
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0 <2.3.29

## Details
Apache Struts 2.x before 2.3.29 allows remote attackers to execute arbitrary code via a "%{}" sequence in a tag attribute, aka forced double OGNL evaluation.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-0785.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4461
- https://github.com/apache/struts
- https://security.netapp.com/advisory/ntap-20180629-0004
- https://struts.apache.org/docs/s2-036.html
