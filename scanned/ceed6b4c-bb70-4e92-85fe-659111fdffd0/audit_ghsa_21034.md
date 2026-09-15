# [H] XWiki.WebHome vulnerable to Improper Privilege Management in XWiki resolving groups

## Summary
Severity: High
Advisory: GHSA-g4h6-qp44-wqvx
CVE: CVE-2022-31166
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-09-20
Source: https://github.com/advisories/GHSA-g4h6-qp44-wqvx
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=11.3.7 <13.10.4
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=14.0-rc-1 <14.2-rc-1

## Details
### Impact

It's possible to exploit a bug in XWikiRights resolution of groups to obtain privilege escalation. 

More specifically, editing a right with the object editor leads to adding a supplementary empty value to groups which is then resolved as a reference to XWiki.WebHome page. Adding an XWikiGroup xobject to that page then transforms it to a group, any user put in that group would then obtain the privileges related to the edited right.

Note that this security issue is normally mitigated by the fact that XWiki.WebHome (and XWiki space in general) should be protected by default for edit rights. 

### Patches

The problem has been patched in XWiki 13.10.4 and 14.2RC1 to not consider anymore empty values in XWikiRights. 

### Workarounds

It's possible to workaround the problem by setting appropriate rights on XWiki.WebHome page to prevent users to edit it. 

### References

* https://jira.xwiki.org/browse/XWIKI-18386
* https://jira.xwiki.org/browse/XWIKI-15776

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-g4h6-qp44-wqvx
- https://nvd.nist.gov/vuln/detail/CVE-2022-31166
- https://github.com/xwiki/xwiki-platform/pull/1800
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-15776
- https://jira.xwiki.org/browse/XWIKI-18386
