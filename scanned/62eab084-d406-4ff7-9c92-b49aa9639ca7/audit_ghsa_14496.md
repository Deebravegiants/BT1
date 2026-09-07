# [C] XWiki Platform vulnerable to privilege escalation via properties with wiki syntax that are executed with wrong author

## Summary
Severity: Critical
Advisory: GHSA-3738-p9x3-mv9r
CVE: CVE-2023-26474
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-3738-p9x3-mv9r
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=13.10 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=13.10 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=14.0 <14.4.7
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=14.0 <14.4.7
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=14.5 <14.10
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=14.5 <14.10

## Details
### Impact

It's possible to use the right of an existing document content author to execute a text area property.

To reproduce:

* As an admin with programming rights, create a new user without script or programming right.
* Login with the freshly created user.
* Insert the following text in source mode in the about section:
```
    {{groovy}}println("hello from groovy!"){{/groovy}}
```
* Click "Save & View"

### Patches

This has been patched in XWiki 14.10, 14.4.7, and 13.10.11.

### Workarounds

No known workaround.

### References
https://jira.xwiki.org/browse/XWIKI-20373

### For more information
If you have any questions or comments about this advisory:

* Open an issue in [Jira](http://jira.xwiki.org/)
* Email us at [Security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-3738-p9x3-mv9r
- https://nvd.nist.gov/vuln/detail/CVE-2023-26474
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20373
