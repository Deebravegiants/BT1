# [H] Rating Script Service expose XWiki to SQL injection

## Summary
Severity: High
Advisory: GHSA-79rg-7mv3-jrr5
CVE: CVE-2021-21380
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-03-23
Source: https://github.com/advisories/GHSA-79rg-7mv3-jrr5
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-ratings-api` — affected >=0 <12.9

## Details
### Impact
This issue impacts only XWiki with the Ratings API installed.
The Rating Script Service expose an API to perform SQL requests without escaping the from and where search arguments. 
This might lead to an SQL script injection quite easily for any user having Script rights on XWiki.

### Patches
The problem has been patched in XWiki 12.9RC1.

### Workarounds
The only workaround besides upgrading XWiki would be to uninstall the Ratings API in XWiki from the Extension Manager.

### References
https://jira.xwiki.org/browse/XWIKI-17662

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](http://jira.xwiki.org)
* Email us at our [security mailing list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-79rg-7mv3-jrr5
- https://nvd.nist.gov/vuln/detail/CVE-2021-21380
- https://jira.xwiki.org/browse/XWIKI-17662
