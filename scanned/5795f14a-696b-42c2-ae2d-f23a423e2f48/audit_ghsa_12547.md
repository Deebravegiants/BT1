# [H] XWiki Platform vulnerable to privilege escalation (PR) from account through TipsPanel

## Summary
Severity: High
Advisory: GHSA-h7cw-44vp-jq7h
CVE: CVE-2023-35166
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-h7cw-44vp-jq7h
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-help-ui` — affected >=8.1-milestone-1 <14.10.5
- Maven: `org.xwiki.platform:xwiki-platform-help-ui` — affected >=15.0-rc-1 <15.1-rc-1

## Details
### Impact

It's possible to execute any wiki content with the right of the TipsPanel author by creating a tip UI extension.

To reproduce:
* Add an object of type UIExtensionClass
* Set "Extension Point ID" to org.xwiki.platform.help.tipsPanel
* Set "Extension ID" to org.xwiki.platform.user.test (needs to be unique but otherwise doesn't matter)
* Set "Extension Parameters" to
    ```
    tip={{async async="true" cached="false" context="doc.reference"}}{{groovy}}println("Hello " + "from groovy!"){{/groovy}}{{/async}}
    ```
* Set "Extension Scope" to "Current User".
* Click "Save & View"
* Open the "Help.TipsPanel" document at <xwiki-host>/xwiki/bin/view/Help/TipsPanel where <xwiki-host> is the URL of your XWiki installation and press refresh repeatedly.

The groovy macro is executed, after the fix you get an error instead.

### Patches

This has been patched in XWiki 15.1-rc-1 and 14.10.5.

### Workarounds

There are no known workarounds for it.

### References

* https://jira.xwiki.org/browse/XWIKI-20281
* https://github.com/xwiki/xwiki-platform/commit/98208c5bb1e8cdf3ff1ac35d8b3d1cb3c28b3263#diff-4e3467d2ef3871a68b2f910e67cf84531751b32e0126321be83c0f1ed5d90b29L176-R178

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-h7cw-44vp-jq7h
- https://nvd.nist.gov/vuln/detail/CVE-2023-35166
- https://github.com/xwiki/xwiki-platform/commit/98208c5bb1e8cdf3ff1ac35d8b3d1cb3c28b3263#diff-4e3467d2ef3871a68b2f910e67cf84531751b32e0126321be83c0f1ed5d90b29L176-R178
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20281
