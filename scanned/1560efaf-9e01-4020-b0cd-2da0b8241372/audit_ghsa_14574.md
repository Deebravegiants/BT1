# [C] org.xwiki.platform:xwiki-platform-panels-ui vulnerable to Eval Injection

## Summary
Severity: Critical
Advisory: GHSA-qxjg-jhgw-qhrv
CVE: CVE-2023-27479
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-08
Source: https://github.com/advisories/GHSA-qxjg-jhgw-qhrv
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-panels-ui` — affected >=6.3-milestone-2 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-panels-ui` — affected >=14.0 <14.4.7
- Maven: `org.xwiki.platform:xwiki-platform-panels-ui` — affected >=14.5 <14.10-rc-1

## Details
### Impact
Any user with view rights can execute arbitrary Groovy, Python or Velocity code in XWiki leading to full access to the XWiki installation. The root cause is improper escaping of UIX parameters

A proof of concept exploit is to log in, add an `XWiki.UIExtensionClass` xobject to the user profile page, with an Extension Parameters content of:

```
order=100
label={{/html}} {{async async="true" cached="false" context="doc.reference"}}{{groovy}}println("Hello " + "from groovy!"){{/groovy}}{{/async}}
icon=icon:pencil
target=XWiki.username
```

Then, navigating to `PanelsCode.ApplicationsPanelConfigurationSheet` (i.e., `<xwiki-host>/xwiki/bin/view/PanelsCode/ApplicationsPanelConfigurationSheet` where `<xwiki-host>` is the URL of your XWiki installation) should not execute the Groovy script. If it does, you will see `Hello from groovy!` displayed on the screen.

### Patches
The vulnerability has been patched in XWiki 13.10.11, 14.4.7 and 14.10-rc-1

### Workarounds
The issue can be fixed by editing the `PanelsCode.ApplicationsPanelConfigurationSheet` wiki page and making the same modifications  as shown in the [patch](https://github.com/xwiki/xwiki-platform/commit/6de5442f3c91c3634a66c7b458d5b142e1c2a2dc) for this issue.

### References
* https://github.com/xwiki/xwiki-platform/commit/6de5442f3c91c3634a66c7b458d5b142e1c2a2dc
* https://jira.xwiki.org/browse/XWIKI-20294

### For more information
If you have any questions or comments about this advisory:
*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-qxjg-jhgw-qhrv
- https://nvd.nist.gov/vuln/detail/CVE-2023-27479
- https://github.com/xwiki/xwiki-platform/commit/6de5442f3c91c3634a66c7b458d5b142e1c2a2dc
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20294
