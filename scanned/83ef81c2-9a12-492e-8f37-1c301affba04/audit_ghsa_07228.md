# [M] org.xwiki.contrib:discussions-server has Cross-Site Request Forgery (CSRF) issue that makes it possible to delete messages

## Summary
Severity: Medium
Advisory: GHSA-4j38-rw27-97gx
CVE: CVE-2023-37465
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-27
Source: https://github.com/advisories/GHSA-4j38-rw27-97gx
Type: github-advisory

## Affected
- Maven: `org.xwiki.contrib:discussions-server` — affected >=0 <2.0-rc-1

## Details
### Impact
It's possible to forge a request to delete a message. 

### Patches
The problem has been patched in version 2.0-rc-1 of Discussion Extension.

### Workarounds
There's no easy workaround except upgrading.

### References
https://jira.xwiki.org/browse/DISCUSSION-22

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [security mailing-list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki-contrib/application-discussions/security/advisories/GHSA-4j38-rw27-97gx
- https://github.com/xwiki-contrib/application-discussions
- https://jira.xwiki.org/browse/DISCUSSION-22
