# [M] apollo-portal has potential CSRF issue

## Summary
Severity: Medium
Advisory: GHSA-fmxq-v8mg-qh25
CVE: CVE-2023-25569
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-02-22
Source: https://github.com/advisories/GHSA-fmxq-v8mg-qh25
Type: github-advisory

## Affected
- Maven: `com.ctrip.framework.apollo:apollo` — affected >=0 <2.1.0

## Details
### Impact
A low-privileged user can create a special web page. If an authenticated portal admin visits this page, the page can silently send a request to assign new roles for that user without any confirmation from the Portal admin.

### Patches
Cookie SameSite strategy was set to Lax in #4664 and was released in [v2.1.0](https://github.com/apolloconfig/apollo/releases/tag/v2.1.0).

### Workarounds
To fix the potential issue without upgrading, simply follow the advice that does not visit unknown source pages.

### References
[Apollo Security Guidence](https://www.apolloconfig.com/#/en/usage/apollo-user-guide?id=_71-security-related)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [issue](https://github.com/apolloconfig/apollo/issues)
* Email us at [apollo-config@googlegroups.com](mailto:apollo-config@googlegroups.com)

## References
- https://github.com/apolloconfig/apollo/security/advisories/GHSA-fmxq-v8mg-qh25
- https://nvd.nist.gov/vuln/detail/CVE-2023-25569
- https://github.com/apolloconfig/apollo/pull/4664
- https://github.com/apolloconfig/apollo/commit/00d968a7229f809b0d8ed0532e8c01a6c2b7c750
- https://github.com/apolloconfig/apollo
- https://github.com/apolloconfig/apollo/releases/tag/v2.1.0
- https://www.apolloconfig.com/#/en/usage/apollo-user-guide?id=_71-security-related
