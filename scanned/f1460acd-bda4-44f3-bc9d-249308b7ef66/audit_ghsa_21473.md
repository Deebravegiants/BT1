# [C] Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection') in AttachmentSelector.xml

## Summary
Severity: Critical
Advisory: GHSA-9hqh-fmhg-vq2j
CVE: CVE-2022-41928
CWE: CWE-95
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-9hqh-fmhg-vq2j
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-attachment-ui` — affected >=5.0-milestone-1 <13.10.7
- Maven: `org.xwiki.platform:xwiki-platform-attachment-ui` — affected >=14.0.0 <14.4.2

## Details
### Impact
Any user with the right to edit his personal page can follow one of the scenario below:

**Scenario 1**:
- Log in as a simple user with just edit rights on the user profile
- Go to the user's profile
- Upload an attachment in the attachment tab at the bottom of the page (any image is fine)
- Click on "rename" in the attachment list and enter `{{async async="true" cached="false" context="doc.reference"}}{{groovy}}println("Hello from groovy!"){{/groovy}}{{/async}}.png` as new attachment name and submit the rename
- Go back to the user profile
- Click on the edit icon on the user avatar
- `Hello from groovy!` is displayed as the title of the attachment

**Scenario 2**:
- Log in as a simple user with just edit rights on a page
- Create a Page `MyPage.WebHome`
- Create an XClass field of type String named `avatar`
- Add an XObject of type `MyPage.WebHome` on the page
- Insert an `attachmentSelector` macro in the document with the following values:
  - **classname**: `MyPage.WebHome`
  - **property**: `avatar`
  - **savemode**: `direct`
  - **displayImage**: `true`
  - **width**: `]] {{async async="true" cached="false" context="doc.reference"}}{{groovy}}println("Hello from groovy!"){{/groovy}}{{/async}}`. You'll find below a snippet of an `attachmentSelector` macro declaration.
- Display the page
- Use the attachment picker to select an image
- `Hello from groovy` is displayed aside the image

Example of an `attachmentSelector` macro declaration:
```
`{{attachmentSelector classname="MyPage.WebHome" property="avatar" savemode="direct" displayImage="true" width="]] {{async async=~"true~" cached=~"false~" context=~"doc.reference~"~}~}{{groovy~}~}println(~"Hello from groovy!~"){{/groovy~}~}{{/async~}~}"/}}`
```

**Note**: The issue can also be reproduced by inserting the dangerous payload in the `height` or `alt` macro properties.

### Patches
The issue can be fixed on a running wiki by updating `XWiki.AttachmentSelector` with the versions below:

- 14.5-rc-1+: https://github.com/xwiki/xwiki-platform/commit/eb15147adf94bddb92626f862c1710d45bcd64a7#diff-e1513599ab698991f6cbba55d38f3f464432ced8d137a668b1f7618c7e747e23
- 14.4.2+: https://github.com/xwiki/xwiki-platform/commit/c02f8eb1f3c953d124f2c097021536f8bc00fa8d#diff-e1513599ab698991f6cbba55d38f3f464432ced8d137a668b1f7618c7e747e23
- 13.10.7+: https://github.com/xwiki/xwiki-platform/commit/efd0df0468d46149ba68b66660b93f31b6318515#diff-e1513599ab698991f6cbba55d38f3f464432ced8d137a668b1f7618c7e747e23

### Workarounds
No known workaround.

### References
- https://jira.xwiki.org/browse/XWIKI-19800

### For more information
If you have any questions or comments about this advisory:
- Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
- Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-9hqh-fmhg-vq2j
- https://nvd.nist.gov/vuln/detail/CVE-2022-41928
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19800
