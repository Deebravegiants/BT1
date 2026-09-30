# [C] Code injection in oscore

## Summary
Severity: Critical
Advisory: GHSA-859m-2pfx-fwhf
CVE: CVE-2023-39022
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-859m-2pfx-fwhf
Type: github-advisory

## Affected
- Maven: `opensymphony:oscore` — affected >=0

## Details
oscore v2.2.6 and below was discovered to contain a code injection vulnerability in the component com.opensymphony.util.EJBUtils.createStateless. This vulnerability is exploited via passing an unchecked argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39022
- https://github.com/LetianYuan/My-CVE-Public-References/tree/main/opensymphony_oscore
