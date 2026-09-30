# [M] Exposure of Sensitive Information to an Unauthorized Actor in org.xwiki.platform:xwiki-platform-livetable-ui

## Summary
Severity: Medium
Advisory: GHSA-p2x4-6ghr-6vmq
CVE: CVE-2022-41935
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-p2x4-6ghr-6vmq
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=12.10.11 <13.10.8
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=14.0.0 <14.4.3
- Maven: `org.xwiki.platform:xwiki-platform-livetable-ui` — affected >=14.5.0 <14.6-rc-1

## Details
### Impact

User without the right to view documents can deduce their existence by repeated Livetable queries.

#### Reproduction steps

1. Restrict "view" access to `Sandbox.TestPage3` by setting an explicit view right for admins
1. As a user who is not an admin, open `<server>/bin/get/XWiki/LiveTableResults?outputSyntax=plain&classname=&collist=doc.title%2Cdoc.location%2Cdoc.content&doc.title=Sandbo&doc.location=Sandbox.TestPage3&doc.content=dummy&limit=0` where `<server>` is the URL of your XWiki installation.

#### Expect Result:

No results are displayed as the user doesn't have view rights on Sandbox.TestPage3.

##### Actual Result:

The result

```json
{
  "reqNo": null,
  "matchingtags": {},
  "tags": [],
  "totalrows": 1,
  "returnedrows": 0,
  "offset": 1,
  "rows": [
    {
      "doc_viewable": false,
      "doc_fullName": "obfuscated"
    }
  ]
}
```

is displayed.

This reveals that a document `Sandbox.TestPage3` exists (we explicitly searched for this name) which has a title containing `"Sandbo"` and a content containing `"dummy"`. By starting with a single letter and then iteratively extending the match, the full content of the title/content or XObject properties can be discovered. Several tests can be combined in a single request to use binary search to narrow down the actual match from a list of possible characters/words. If the used alphabet is known and smaller than 128 distinct characters, it is possible to discover one character with 7 requests. Alternatively, frequencies of words and word pairs (2-gram frequencies) can be used to first guess whole words and only resort to guessing individual characters if none of the predicted words match, allowing a much faster recovery of the textual content. As it also depends on the content how easy the attack is and how much recovered content would be a "successful" attack, it is hard to quantify how many requests are necessary.

### Patches

The issue has been patched in XWiki 14.6RC1, 13.10.8, and 14.4.3, the response is not properly cleaned up of obfuscated entries.

### Workarounds

The [patch](https://github.com/xwiki/xwiki-platform/commit/1450b6e3c69ac7df25e5a2571186d1f43402facd#diff-5a739e5865b1f1ad9d79b724791be51b0095a0170cc078911c940478b13b949a) for the document `XWiki.LiveTableResultsMacros` can be manually applied or a XAR archive of a patched version can be [imported](https://www.xwiki.org/xwiki/bin/view/Documentation/UserGuide/Features/Imports#HImportingXWikipages), on versions >= 12.10.11, >= 13.9-rc-1, and >= 13.4.4.

### References

- https://github.com/xwiki/xwiki-platform/commit/1450b6e3c69ac7df25e5a2571186d1f43402facd#diff-5a739e5865b1f1ad9d79b724791be51b0095a0170cc078911c940478b13b949a
- https://jira.xwiki.org/browse/XWIKI-19999

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
- Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-p2x4-6ghr-6vmq
- https://nvd.nist.gov/vuln/detail/CVE-2022-41935
- https://github.com/xwiki/xwiki-platform/commit/1450b6e3c69ac7df25e5a2571186d1f43402facd#diff-5a739e5865b1f1ad9d79b724791be51b0095a0170cc078911c940478b13b949a
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19999
