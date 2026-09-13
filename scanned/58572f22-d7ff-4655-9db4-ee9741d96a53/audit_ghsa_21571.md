# [M] Missing Authorization in User#setDisabledStatus in org.xwiki.platform:xwiki-platform-oldcore

## Summary
Severity: Medium
Advisory: GHSA-2gj2-vj98-j2qq
CVE: CVE-2022-41929
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-2gj2-vj98-j2qq
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=11.7RC1 <13.10.7
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=14.0.0 <14.4.2

## Details
### Impact

It's possible for a user with only Script rights to enable or disable a user: this operation should be only doable for users with admin rights. 

### Patches

This problem has been patched in XWiki 13.10.7, 14.4.2 and 14.5RC1.

### Workarounds

There is no workaround other than upgrading the wiki, but note that this only impacts users with Script rights: administrator should take care which users have such right. 

### References

  * https://jira.xwiki.org/browse/XWIKI-19804
  * https://github.com/xwiki/xwiki-platform/commit/0b732f2ef0224e2aaf10e2e1ef48dbd3fb6e10cd

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [JIRA](https://jira.xwiki.org)
* Email us at [security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-2gj2-vj98-j2qq
- https://nvd.nist.gov/vuln/detail/CVE-2022-41929
- https://github.com/xwiki/xwiki-platform/commit/0b732f2ef0224e2aaf10e2e1ef48dbd3fb6e10cd
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19804
