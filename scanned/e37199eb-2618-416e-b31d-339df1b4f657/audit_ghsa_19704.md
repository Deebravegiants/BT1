# [H] The WikiManager REST API allows any user to create wikis

## Summary
Severity: High
Advisory: GHSA-gfp2-6qhm-7x43
CVE: CVE-2025-29926
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-gfp2-6qhm-7x43
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-wiki-rest-default` — affected >=5.4-rc-1 <15.10.15
- Maven: `org.xwiki.platform:xwiki-platform-wiki-rest-default` — affected >=16.0.0-rc-1 <16.4.6
- Maven: `org.xwiki.platform:xwiki-platform-wiki-rest-default` — affected >=16.5.0-rc-1 <16.10.0

## Details
### Impact

Any user can exploit the WikiManager REST API to create a new wiki, where the user could become an administrator and so performs other attacks on the farm.
Note that this REST API is not bundled in XWiki Standard by default: it needs to be installed manually through the extension manager.

### Patches

The problem has been patched in versions 15.10.15, 16.4.6 and 16.10.0 of the REST module.

### Workarounds

There's no workaround other than upgrading the dependency.

### References

 * JIRA ticket: https://jira.xwiki.org/browse/XWIKI-22490
 * Commit of the fix: https://github.com/xwiki/xwiki-platform/commit/82aa670106c7f5e6238ca6ed59a52d1800e05b99

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

You can specify here who reported the issue.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-gfp2-6qhm-7x43
- https://nvd.nist.gov/vuln/detail/CVE-2025-29926
- https://github.com/xwiki/xwiki-platform/commit/82aa670106c7f5e6238ca6ed59a52d1800e05b99
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-22490
