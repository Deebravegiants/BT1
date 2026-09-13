# [H] Apache MyFaces Vulnerable to EL Injection

## Summary
Severity: High
Advisory: GHSA-jq6g-p65r-44xr
CVE: CVE-2011-4343
CWE: CWE-200, CWE-917
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jq6g-p65r-44xr
Type: github-advisory

## Affected
- Maven: `org.apache.myfaces.core:myfaces-core-module` — affected >=2.0.1 <2.0.11
- Maven: `org.apache.myfaces.core:myfaces-core-module` — affected >=2.1.0 <2.1.5

## Details
Information disclosure vulnerability in Apache MyFaces Core 2.0.1 through 2.0.10 and 2.1.0 through 2.1.4 allows remote attackers to inject EL expressions via crafted parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4343
- https://github.com/apache/myfaces/commit/a74b551b2ce6e88101ff453389a761f230e428a1
- https://github.com/apache/myfaces/commit/caee86e71ab8c5f038186158e9955887ed72a0fd
- https://github.com/apache/myfaces
- https://issues.apache.org/jira/secure/attachment/12504807/MYFACES-3405-1.patch
- http://marc.info/?l=full-disclosure&m=132313252814362
