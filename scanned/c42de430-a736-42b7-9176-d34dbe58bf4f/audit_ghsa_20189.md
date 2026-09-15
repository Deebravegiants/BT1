# [C] Server-Side Template Injection in formio

## Summary
Severity: Critical
Advisory: GHSA-52vj-mr2j-f8jh
CVE: CVE-2020-28246
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-52vj-mr2j-f8jh
Type: github-advisory

## Affected
- npm: `formio` — affected >=0

## Details
A Server-Side Template Injection (SSTI) was discovered in Form.io 2.0.0. This leads to Remote Code Execution during deletion of the default Email template URL. NOTE: the email templating service was removed after 2020. Additionally, the vendor disputes this issue indicating this is sandboxed and only executable by admins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28246
- https://github.com/formio/enterprise-release/blob/master/API-Server-Change-Log.md
- https://github.com/formio/formio
