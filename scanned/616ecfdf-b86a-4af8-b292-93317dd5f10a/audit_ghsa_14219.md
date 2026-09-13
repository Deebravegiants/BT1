# [C] XWiki vulnerable to Code Injection in template provider administration

## Summary
Severity: Critical
Advisory: GHSA-9j36-3cp4-rh4j
CVE: CVE-2023-29514
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-9j36-3cp4-rh4j
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform.applications:xwiki-application-administration` — affected >=1.35
- Maven: `org.xwiki.platform:xwiki-platform-administration` — affected >=3.1-milestone-1
- Maven: `org.xwiki.platform:xwiki-platform-administration-ui` — affected >=4.2-milestone-1 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-administration-ui` — affected >=14.0-rc-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-administration-ui` — affected >=14.5 <14.10.1

## Details
### Impact

Any user with edit rights on any document (e.g., the own user profile) can execute code with programming rights, leading to remote code execution by following these steps:

1. Set the title of any document you can edit (can be the user profile) to
```
    {{async async="true" cached="false" context="doc.reference"}}{{groovy}}println("Hello " + "from groovy!"){{/groovy}}{{/async}}
```
2. Use the object editor to add an object of type `XWiki.TemplateProviderClass` (named "Template Provider Class") to that document.
3. Go to another document you can view (can be the home page) and append `?sheet=XWiki.AdminTemplatesSheet` to the URL.

When the attack is successful, a template with name "Hello from groovy!" is displayed in the list while on fixed systems, the full title should be displayed.

### Patches

This vulnerability has been patched in XWiki 13.10.11, 14.4.8, 14.10.1 and 15.0 RC1.

### Workarounds

The vulnerability can be fixed by patching the code in the affected XWiki document as shown in the [patch](https://github.com/xwiki/xwiki-platform/commit/7bf7094f8ffac095f5d66809af7554c9cc44de09).

### References

* https://jira.xwiki.org/browse/XWIKI-20268
* https://github.com/xwiki/xwiki-platform/commit/7bf7094f8ffac095f5d66809af7554c9cc44de09

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-9j36-3cp4-rh4j
- https://nvd.nist.gov/vuln/detail/CVE-2023-29514
- https://github.com/xwiki/xwiki-platform/commit/7bf7094f8ffac095f5d66809af7554c9cc44de09
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20268
