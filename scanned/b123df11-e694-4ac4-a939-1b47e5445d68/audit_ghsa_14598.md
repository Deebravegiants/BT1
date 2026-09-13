# [C] XWiki Platform may allow privilege escalation to programming rights via user's first name

## Summary
Severity: Critical
Advisory: GHSA-8cw6-4r32-6r3h
CVE: CVE-2023-26055
CWE: CWE-150
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-8cw6-4r32-6r3h
Type: github-advisory

## Affected
- Maven: `org.xwiki.commons:xwiki-commons-xml` — affected >=3.1-milestone-1 <13.10.9
- Maven: `org.xwiki.commons:xwiki-commons-xml` — affected >=14.0-rc-1 <14.4.4
- Maven: `org.xwiki.commons:xwiki-commons-xml` — affected >=14.5 <14.7-rc-1

## Details
### Impact
Any user can edit his own profile and inject code which is going to be executed with programming right.

Steps to reproduce:

* Set your first name to

```
    {{cache id="userProfile"}}{{groovy}}println("Hello from groovy!"){{/groovy}}{{/cache}}
```

The first name appears as interpreted "`Hello from groovy`" instead of the expected fully escaped "`{{cache id="userProfile"}}{{groovy}}println("Hello from groovy!"){{/groovy}}{{/cache}}`".

The same vulnerability can also be exploited in all other places where short text properties are displayed, e.g., in apps created using [Apps Within Minutes](https://extensions.xwiki.org/xwiki/bin/view/Extension/App%20Within%20Minutes%20Application) that use a short text field.

### Patches
The problem has been patched on versions 13.10.9, 14.4.4, 14.7RC1.

### Workarounds
There are no other workarounds than upgrading XWiki or patching the xwiki-commons-xml JAR file.

### References
* https://jira.xwiki.org/browse/XWIKI-19793
* https://jira.xwiki.org/browse/XWIKI-19794
* https://jira.xwiki.org/browse/XCOMMONS-2498

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-commons/security/advisories/GHSA-8cw6-4r32-6r3h
- https://nvd.nist.gov/vuln/detail/CVE-2023-26055
- https://github.com/xwiki/xwiki-commons
- https://jira.xwiki.org/browse/XCOMMONS-2498
- https://jira.xwiki.org/browse/XWIKI-19793
- https://jira.xwiki.org/browse/XWIKI-19794
