# [C] XWiki Platform's async and display macro allow displaying and interacting with any document in restricted mode

## Summary
Severity: Critical
Advisory: GHSA-gpq5-7p34-vqx5
CVE: CVE-2023-29526
CWE: CWE-284, CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-20
Source: https://github.com/advisories/GHSA-gpq5-7p34-vqx5
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=10.11.1 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=14.0-rc-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=14.5 <14.10.3
- Maven: `org.xwiki.platform:xwiki-platform-rendering-async-macro` — affected >=10.11.1 <13.10.11
- Maven: `org.xwiki.platform:xwiki-platform-rendering-async-macro` — affected >=14.0-rc-1 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-rendering-async-macro` — affected >=14.5 <14.10.3

## Details
### Impact

It's possible to display any page you cannot access through the combination of the async and display macro. 

Steps to reproduce:

1. Enable comments for guests by giving guests comment rights
2. As a guest, create a comment with content ```{{async}}{{display reference="Menu.WebHome" /}}{{/async}}```
3. Open the comments viewer from the menu (appends ?viewer=comments to the URL)

-> the `Menu.WebHome` is displayed while the expectation would be to have an error that the current user is not allowed to see it

### Patches

The vulnerability has been patched in XWiki 15.0-rc-1, 14.10.3, 14.4.8, and 13.10.11.

### Workarounds

There is no known workaround.

### References

https://jira.xwiki.org/browse/XWIKI-20394
https://jira.xwiki.org/browse/XRENDERING-694

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-gpq5-7p34-vqx5
- https://nvd.nist.gov/vuln/detail/CVE-2023-29526
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XRENDERING-694
- https://jira.xwiki.org/browse/XWIKI-20394
