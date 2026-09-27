# [H] XWiki Platform vulnerable to CSRF privilege escalation/RCE via the create action

## Summary
Severity: High
Advisory: GHSA-4f8m-7h83-9f6m
CVE: CVE-2023-40572
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-23
Source: https://github.com/advisories/GHSA-4f8m-7h83-9f6m
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=3.2-milestone-3 <14.10.9
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.0-rc-1 <15.4-rc-1

## Details
### Impact
The create action is vulnerable to a CSRF attack, allowing script and thus remote code execution when targeting a user with script/programming right, thus compromising the confidentiality, integrity and availability of the whole XWiki installation. To reproduce, the XWiki syntax `[[image:path:/xwiki/bin/create/Foo/WebHome?template=&parent=Main.WebHome&title=$services.logging.getLogger(%22foo%22).error(%22Script%20executed!%22)]]` can be added to any place that supports XWiki syntax like a comment. When a user with script right views this image and a log message `ERROR foo - Script executed!` appears in the log, the XWiki installation is vulnerable.

### Patches
This has been patched in XWiki 14.10.9 and 15.4RC1 by requiring a CSRF token for the actual page creation.

### Workarounds
There are no known workarounds.

### References
* https://jira.xwiki.org/browse/XWIKI-20849
* https://github.com/xwiki/xwiki-platform/commit/4b20528808d0c311290b0d9ab2cfc44063380ef7

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-4f8m-7h83-9f6m
- https://nvd.nist.gov/vuln/detail/CVE-2023-40572
- https://github.com/xwiki/xwiki-platform/commit/123e5d7e4ca06bf75b95aaef665aafc4fa9cae64
- https://github.com/xwiki/xwiki-platform/commit/4b20528808d0c311290b0d9ab2cfc44063380ef7
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20849
