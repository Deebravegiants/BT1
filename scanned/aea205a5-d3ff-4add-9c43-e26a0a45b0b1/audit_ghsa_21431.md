# [C] Missing Authorization to enable or disable users in org.xwiki.platform:xwiki-platform-user-profile-ui

## Summary
Severity: Critical
Advisory: GHSA-p5v9-g8w8-5q4v
CVE: CVE-2022-41930
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-p5v9-g8w8-5q4v
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-user-profile-ui` — affected >=12.4 <13.10.7
- Maven: `org.xwiki.platform:xwiki-platform-user-profile-ui` — affected >=14.0.0 <14.4.2

## Details
### Impact

Any user (logged in or not) with access to the page XWiki.XWikiUserProfileSheet can enable or disable any user profile. This might allow to a disabled user to re-enable themselves, or to an attacker to disable any user of the wiki. 

### Patches

The problem has been patched in XWiki 13.10.7, 14.5RC1 and 14.4.2. 

### Workarounds

The problem can be patched immediately by editing the page `XWiki.XWikiUserProfileSheet` in the wiki and by performing the changes contained in https://github.com/xwiki/xwiki-platform/commit/5be1cc0adf917bf10899c47723fa451e950271fa.

### References

  * https://github.com/xwiki/xwiki-platform/commit/5be1cc0adf917bf10899c47723fa451e950271fa
  * https://jira.xwiki.org/browse/XWIKI-19792

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [JIRA](https://jira.xwiki.org)
* Email us at [security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-p5v9-g8w8-5q4v
- https://nvd.nist.gov/vuln/detail/CVE-2022-41930
- https://github.com/xwiki/xwiki-platform/commit/5be1cc0adf917bf10899c47723fa451e950271fa
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19792
