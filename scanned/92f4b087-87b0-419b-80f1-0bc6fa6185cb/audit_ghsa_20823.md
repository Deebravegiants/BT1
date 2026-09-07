# [H] XWiki Platform Web Templates vulnerable to Unauthorized User Registration Through the Distribution Wizard

## Summary
Severity: High
Advisory: GHSA-h5j3-5x63-p8jv
CVE: CVE-2022-36093
CWE: CWE-287, CWE-288
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-h5j3-5x63-p8jv
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=0 <13.10.5
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=8.0-rc-1 <13.10.5
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=14.0 <14.3-rc-1
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=14.0 <14.3-rc-1

## Details
### Impact
By passing a template of the distribution wizard to the xpart template, user accounts can be created even when user registration is disabled. This also circumvents any email verification. Before versions 14.2 and 13.10.4, this can also be exploited on a private wiki, thus potentially giving the attacker access to the wiki. Depending on the configured default rights of users, this could also give attackers write access to an otherwise read-only public wiki. Users can also be created when an external authentication system like LDAP is configured, but authentication fails unless the authentication system supports a bypass/local accounts are enabled in addition to the external authentication system.

### Patches
This issue has been patched in XWiki 13.10.5 and 14.3RC1.

### Workarounds
It is possible to replace `xpart.vm`, the entry point for this attack, by a patched version from the [patch](https://github.com/xwiki/xwiki-platform/commit/70c64c23f4404f33289458df2a08f7c4be022755) without updating XWiki.

### References
* https://jira.xwiki.org/browse/XWIKI-19558

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-h5j3-5x63-p8jv
- https://nvd.nist.gov/vuln/detail/CVE-2022-36093
- https://github.com/xwiki/xwiki-platform/commit/70c64c23f4404f33289458df2a08f7c4be022755
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19558
