# [H] XWiki Platform vulnerable to reflected cross-site scripting via delattachment action

## Summary
Severity: High
Advisory: GHSA-phwm-87rg-27qq
CVE: CVE-2023-35157
CWE: CWE-79, CWE-80
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-phwm-87rg-27qq
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=3.2-milestone-3 <14.10.6
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=15.0-rc-0 <15.1-rc-1

## Details
### Impact
It's possible to perform an XSS by forging a request to a delete attachment action with a specific attachment name. 
Now this XSS can be exploited only if the attacker knows the CSRF token of the user, or if the user ignores the warning about the missing CSRF token. 

### Patches

The vulnerability has been patched in XWiki 15.1-rc-1 and XWiki 14.10.6.


### Workarounds

There's no workaround for this other than upgrading XWiki. 

### References

  * Jira ticket: https://jira.xwiki.org/browse/XWIKI-20339
  * Commit containing the fix: https://github.com/xwiki/xwiki-platform/commit/35e9073ffec567861e0abeea072bd97921a3decf

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-phwm-87rg-27qq
- https://nvd.nist.gov/vuln/detail/CVE-2023-35157
- https://github.com/xwiki/xwiki-platform/commit/35e9073ffec567861e0abeea072bd97921a3decf
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20339
