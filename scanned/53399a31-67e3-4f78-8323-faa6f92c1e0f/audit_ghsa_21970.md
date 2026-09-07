# [H] Remote code execution in xwiki-platform

## Summary
Severity: High
Advisory: GHSA-mgjw-2wrp-r535
CVE: CVE-2022-23616
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-mgjw-2wrp-r535
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-administration-ui` — affected >=3.1-milestone-1 <13.1RC1

## Details
### Impact
It's possible for an unprivileged user to perform a remote code execution by injecting a groovy script in her own profile and by calling the Reset password feature since the feature is performing a save of the user profile with programming rights in the impacted versions of XWiki.

### Patches
The problem has been patched in XWiki 13.1RC1 with a complete refactoring of the Reset password feature.

### Workarounds
There's different possible workarounds, all consisting in modifying the XWiki/ResetPassword page.
  - the Reset password feature can be entirely disabled by deleting the XWiki/ResetPassword page
  - the script in XWiki/ResetPassword can also be modified or removed: an administrator can replace it with a simple email contact to ask an administrator to reset the password. 

### References
https://jira.xwiki.org/browse/XWIKI-16661

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira](https://jira.xwiki.org)
* Email us at [Security mailing-list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-mgjw-2wrp-r535
- https://nvd.nist.gov/vuln/detail/CVE-2022-23616
- https://github.com/xwiki/xwiki-platform/commit/407caeba05c181bd4835e1dd12e431fa15ff728b#diff-c51a3675b6e312a9385a27566bfb4e5cL340
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-16661
