# [C] XSS Cross Site Scripting

## Summary
Severity: Critical
Advisory: GHSA-5c66-v29h-xjh8
CVE: CVE-2021-29459
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2021-04-22
Source: https://github.com/advisories/GHSA-5c66-v29h-xjh8
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=0 <12.6.3
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=12.6.4 <12.8
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=0 <12.6.3
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=12.6.4 <12.8

## Details
### Impact
It is possible to persistently inject scripts in XWiki.

For unregistred users:
- By filling simple text fields

For registered users:
- By filling their personal information
- (if they have edit rights) By filling the values of static lists using App Within Minutes

That can lead to user's session hijacking, and if used in conjunction with a social engineering attack it can also lead to disclosure of sensitive data, CSRF attacks and other security vulnerabilities.
That can also lead to the attacker taking over an account.
If the victim has administrative rights it might even lead to code execution on the server, depending on the application and the privileges of the account.
### Patches
It has been patched on XWiki 12.8 and 12.6.3.

### Workarounds
There is no easy workaround except upgrading XWiki.

### References
https://jira.xwiki.org/browse/XWIKI-17374

### For more information
If you have any questions or comments about this advisory:
  * Open an issue in [Jira XWiki](https://jira.xwiki.org)
  * Email us at our [security mailing list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-5c66-v29h-xjh8
- https://nvd.nist.gov/vuln/detail/CVE-2021-29459
