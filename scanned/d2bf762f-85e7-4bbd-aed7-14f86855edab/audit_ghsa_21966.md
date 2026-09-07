# [M] Information exposure in xwiki-platform

## Summary
Severity: Medium
Advisory: GHSA-35fg-hjcr-j65f
CVE: CVE-2022-23619
CWE: CWE-200, CWE-640
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-35fg-hjcr-j65f
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=13.5RC1 <13.6RC1
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=13.0.0 <13.4.1
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=0 <12.10.9

## Details
### Impact
It's possible to guess if a user has an account on the wiki by using the "Forgot your password" form, even if the wiki is closed to guest users.

### Patches
The problem has been patched on XWiki 12.10.9, 13.4.1 and 13.6RC1.

### Workarounds
There's no easy workaround other than applying the upgrade.

### References

https://jira.xwiki.org/browse/XWIKI-18787

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [JIRA](https://jira.xwiki.org)
* Email us at [XWiki Security Mailing list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-35fg-hjcr-j65f
- https://nvd.nist.gov/vuln/detail/CVE-2022-23619
- https://github.com/xwiki/xwiki-platform/commit/d8a3cce48e0ac1a0f4a3cea7a19747382d9c9494
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-18787
