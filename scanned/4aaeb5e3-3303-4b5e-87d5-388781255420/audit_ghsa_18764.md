# [C] XWiki OIDC Authenticator: Users with "view" access can create tokens for any users they can view

## Summary
Severity: Critical
Advisory: GHSA-f2hf-pfrj-vrm7
CVE: CVE-2025-49594
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-06
Source: https://github.com/advisories/GHSA-f2hf-pfrj-vrm7
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib.oidc:oidc-authenticator` — affected >=2.17.1 <2.18.2

## Details
### Impact

Anyone with VIEW access to a user profile can create a token for that user. If that XWiki instance is configured to allow token authentication, it allows authentication with any user (since users are very commonly viewable, at least to other registered users).

### Patches

Version 2.18.2.

### Workarounds

The only workaround is to disable token access.

### References

* https://jira.xwiki.org/browse/OIDC-240
* https://github.com/xwiki-contrib/oidc/commit/d90d717172283aaa96bb5bb44e357f910ae64adb

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki-contrib/oidc/security/advisories/GHSA-f2hf-pfrj-vrm7
- https://nvd.nist.gov/vuln/detail/CVE-2025-49594
- https://github.com/xwiki-contrib/oidc/commit/d90d717172283aaa96bb5bb44e357f910ae64adb
- https://github.com/xwiki-contrib/oidc
- https://jira.xwiki.org/browse/OIDC-240
- https://www.vicarius.io/vsociety/posts/cve-2025-49594-detect-xwiki-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-49594-mitigate-xwiki-vulnerability
