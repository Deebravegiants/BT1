# [C] Expression Language Injection in Apache Struts

## Summary
Severity: Critical
Advisory: GHSA-v8j6-6c2r-r27c
CVE: CVE-2021-31805
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-v8j6-6c2r-r27c
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0 <2.5.30

## Details
The fix issued for CVE-2020-17530 was incomplete. So from Apache Struts 2.0.0 to 2.5.29, still some of the tag’s attributes could perform a double evaluation if a developer applied forced OGNL evaluation by using the %{...} syntax. Using forced OGNL evaluation on untrusted user input can lead to a Remote Code Execution and security degradation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31805
- https://cwiki.apache.org/confluence/display/WW/S2-062
- https://security.netapp.com/advisory/ntap-20220420-0001
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://www.openwall.com/lists/oss-security/2022/04/12/6
