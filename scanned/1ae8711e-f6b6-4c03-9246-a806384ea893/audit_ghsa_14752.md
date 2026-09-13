# [C] XWiki allows RCE from script right in configurable sections

## Summary
Severity: Critical
Advisory: GHSA-r279-47wg-chpr
CVE: CVE-2024-55879
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-12
Source: https://github.com/advisories/GHSA-r279-47wg-chpr
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-administration-ui` — affected >=2.3 <15.10.9
- Maven: `org.xwiki.platform:xwiki-platform-administration-ui` — affected >=16.0.0-rc-1 <16.3.0

## Details
### Impact
Any user with script rights can perform arbitrary remote code execution by adding instances of `XWiki.ConfigurableClass` to any page. This compromises the confidentiality, integrity and availability of the whole XWiki installation.

To reproduce on a instance, as a user with script rights, edit your user profile and add an object of type `XWiki.ConfigurableClass` ("Custom configurable sections").
Set "Display in section" and "Display in category" to `other`, "Scope" to `Wiki and all spaces` and "Heading" to:
```
#set($codeToExecute = 'Test') #set($codeToExecuteResult = '{{async}}{{groovy}}services.logging.getLogger("attacker").error("Attack from Heading succeeded!"){{/groovy}}{{/async}}')
```
Save the page and view it, then add `?sheet=XWiki.AdminSheet&viewer=content&section=other` to the URL.
If the logs contain "attacker - Attack from Heading succeeded!", then the instance is vulnerable.

### Patches
This has been patched in XWiki 15.10.9 and 16.3.0.

### Workarounds
We're not aware of any workaround except upgrading.

### References
* https://jira.xwiki.org/browse/XWIKI-21207
* https://github.com/xwiki/xwiki-platform/commit/8493435ff9606905a2d913607d6c79862d0c168d

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-r279-47wg-chpr
- https://nvd.nist.gov/vuln/detail/CVE-2024-55879
- https://github.com/xwiki/xwiki-platform/commit/8493435ff9606905a2d913607d6c79862d0c168d
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21207
