# [M] Apache Druid vulnerable to Server-Side Request Forgery, Cross-site Scripting, Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-2xcr-p767-f3rv
CVE: CVE-2025-27888
CWE: CWE-601, CWE-79, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-2xcr-p767-f3rv
Type: github-advisory

## Affected
- Maven: `org.apache.druid:druid` — affected >=0 <31.0.2
- Maven: `org.apache.druid:druid` — affected >=32.0.0 <32.0.1

## Details
Severity: medium (5.8) / important

Server-Side Request Forgery (SSRF), Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting'), URL Redirection to Untrusted Site ('Open Redirect') vulnerability in Apache Druid.

This issue affects all previous Druid versions.

When using the Druid management proxy, a request that has a specially crafted URL could be used to redirect the request to an arbitrary server instead. This has the potential for XSS or XSRF. The user is required to be authenticated for this exploit. The management proxy is enabled in Druid's out-of-box configuration. It may be disabled to mitigate this vulnerability. If the management proxy is disabled, some web console features will not work properly, but core functionality is unaffected.

Users are recommended to upgrade to Druid 31.0.2 or Druid 32.0.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27888
- https://github.com/apache/druid
- https://github.com/apache/druid/releases/tag/druid-31.0.2
- https://github.com/apache/druid/releases/tag/druid-32.0.1
- https://lists.apache.org/thread/c0qo989pwtrqkjv6xfr0c30dnjq8vf39
- http://www.openwall.com/lists/oss-security/2025/03/19/7
