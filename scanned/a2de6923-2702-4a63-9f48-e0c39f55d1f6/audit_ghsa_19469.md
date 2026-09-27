# [H] Any user with view access to the XWiki space can change the authenticator

## Summary
Severity: High
Advisory: GHSA-f9c6-2f9p-82jj
CVE: CVE-2025-46557
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-30
Source: https://github.com/advisories/GHSA-f9c6-2f9p-82jj
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-security-authentication-ui` — affected >=15.3-rc-1 <15.10.14
- Maven: `org.xwiki.platform:xwiki-platform-security-authentication-ui` — affected >=16.0.0-rc-1 <16.4.6
- Maven: `org.xwiki.platform:xwiki-platform-security-authentication-ui` — affected >=16.5.0-rc-1 <16.10.0-rc-1

## Details
### Impact

A user who can access pages located in the XWiki space (by default, anyone) can access the page `XWiki.Authentication.Administration` and (unless an authenticator is set in `xwiki.cfg`) switch to another installed authenticator.

Note that, by default, there is only one authenticator available (`Standard XWiki Authenticator`). So, if no authenticator extension was installed, it's not really possible to do anything for an attacker.

Also, in most cases, if you have installed and are using an SSO authenticator (like OIDC or LDAP for example), the worst an attacker can do is break authentication by switching back to the standard authenticator (that's because it's impossible to login to a user which does not have a stored password, and that's usually what SSO authenticator produce).

### Patches

This has been patched in XWiki 15.10.9 and XWiki 16.3.0RC1.

### Workarounds

You can very easily fix this vulnerability in your instance through right configuration:
* access the page and children right administration of the page `XWiki.Authentication` (`https://myhost/xwiki/bin/admin/XWiki/Authentication/WebPreferences?editor=spaceadmin&section=PageAndChildrenRights&space=XWiki.Authentication#|t=usersandgroupstable&p=1&l=10&uorg=groups&wiki=local&clsname=XWiki.XWikiGlobalRights`)
* make sure only admin user have the VIEW right

### References

https://jira.xwiki.org/browse/XWIKI-22604
https://github.com/xwiki/xwiki-platform/commit/5efc31cea1501c9a5cb593566fea8b558ff32a2a

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-f9c6-2f9p-82jj
- https://nvd.nist.gov/vuln/detail/CVE-2025-46557
- https://github.com/xwiki/xwiki-platform/commit/5efc31cea1501c9a5cb593566fea8b558ff32a2a
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22604
