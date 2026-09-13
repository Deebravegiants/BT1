# [H] XWiki Platform packages Expose Sensitive Information to an Unauthorized Actor

## Summary
Severity: High
Advisory: GHSA-5cf8-vrr8-8hjm
CVE: CVE-2023-26476
CWE: CWE-200, CWE-307
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-5cf8-vrr8-8hjm
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=3.2-m3 <13.4.4
- Maven: `org.xwiki.platform:xwiki-platform-wiki-ui-mainwiki` — affected >=3.2-m3 <13.4.4
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=13.5.0 <13.10.9
- Maven: `org.xwiki.platform:xwiki-platform-wiki-ui-mainwiki` — affected >=13.5.0 <13.10.9
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=14.0.0 <14.7-rc-1
- Maven: `org.xwiki.platform:xwiki-platform-wiki-ui-mainwiki` — affected >=14.0.0 <14.7-rc-1

## Details
### Impact
Users can deduce the content of the password fields by repeated call to `LiveTableResults` and `WikisLiveTableResultsMacros`.

### Patches
The issue is applied on versions 14.7-rc-1, 13.4.4, and 13.10.9.

### Workarounds
The issue can be fixed by upgrading to versions 14.7-rc-1, 13.4.4, and 13.10.9 and higher, or in version >= 3.2M3 by applying the patch manually on `LiveTableResults` and `WikisLiveTableResultsMacros`.

### References
- Jira: https://jira.xwiki.org/browse/XWIKI-19949
- Patch: https://github.com/xwiki/xwiki-platform/commit/7f8825537c9523ccb5051abd78014d156f9791c8

### For more information
If you have any questions or comments about this advisory:

- Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
- Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-5cf8-vrr8-8hjm
- https://nvd.nist.gov/vuln/detail/CVE-2023-26476
- https://github.com/xwiki/xwiki-platform/commit/7f8825537c9523ccb5051abd78014d156f9791c8
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19949
