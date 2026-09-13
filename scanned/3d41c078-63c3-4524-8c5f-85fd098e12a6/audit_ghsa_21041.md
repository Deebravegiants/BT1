# [H] XWiki Platform Improper Authorization check for inactive users

## Summary
Severity: High
Advisory: GHSA-jgc8-gvcx-9vfx
CVE: CVE-2022-36090
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-jgc8-gvcx-9vfx
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=1.1 <13.10.5
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=14.0 <14.3-rc-1

## Details
### Impact

Some resources are missing a check for inactive (not yet activated or disabled) users in XWiki, including the REST service: so a disabled user can enable themselves using a REST call. On the same way some resources handler created by extensions are not protected by default: so an inactive users could perform actions for such extensions.

This issue exists since at least version 1.1 of XWiki for instance configured with the email activation required for new users. Now it's more critical for newer versions (>= 11.3RC1) since we provided the capability to disable user without deleting them, and we encouraged using that feature.

### Patches

This issue has been patched in XWiki 14.3RC1 and XWiki 13.10.5. 

### Workarounds

There is no workaround for this other than upgrading XWiki. 

### References

 * https://jira.xwiki.org/browse/XWIKI-19559

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org)
* Email us at [security mailing-list](mailto:security@xwiki.com)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-jgc8-gvcx-9vfx
- https://nvd.nist.gov/vuln/detail/CVE-2022-36090
- https://github.com/xwiki/xwiki-platform/commit/e074d226d9b2b96a0a1ba4349d1b73a802842986
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19559
