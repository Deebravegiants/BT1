# [C] XWiki Platform Mentions UI vulnerable to Cross-site Scripting

## Summary
Severity: Critical
Advisory: GHSA-c5v8-2q4r-5w9v
CVE: CVE-2022-36098
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-c5v8-2q4r-5w9v
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-mentions-ui` — affected >=12.5-rc-1 <13.10.6
- Maven: `org.xwiki.platform:xwiki-platform-mentions-ui` — affected >=14.0 <14.4

## Details
### Impact
It's possible to store Javascript or groovy scripts in an mention macro anchor or reference field. The stored code is executed by anyone visiting the page with the mention.

For example, the example below will create a file at `/tmp/exploit.txt`:

```
{{mention reference="XWiki.Translation" anchor="{{/html~}~}{{async async=~"true~" cached=~"false~" context=~"doc.reference~"~}~}{{groovy~}~}new File(~"/tmp/exploit.txt~").withWriter { out -> out.println(~"owned!~"); }{{/groovy~}~}{{/async~}~}"/}}
```

### Patches
This issue has been patched on XWiki 14.4 and 13.10.6.

### Workarounds
It's possible to fix the vulnerability by updating `XWiki.Mentions.MentionsMacro` and edit the `Macro code` field of the `XWiki.WikiMacroClass` XObject.

```velocity
<a id="$anchor" class="$stringtool.join($cssClasses, ' ')" data-reference="$services.model.serialize($reference.reference, 'default')" href="$link">$content</a>
```

Must be replaced by 

```velocity
<a id="$escapetool.xml($anchor)" class="$stringtool.join($cssClasses, ' ')" data-reference="$escapetool.xml($services.model.serialize($reference.reference, 'default'))" href="$escapetool.xml($link)">
  $escapetool.xml($content)
</a>
```

See the patches:
- 14.4: https://github.com/xwiki/xwiki-platform/commit/4f290d87a8355e967378a1ed6aee23a06ba162eb
- 13.10.6: https://github.com/xwiki/xwiki-platform/commit/4032dc896857597efd169966dc9e2752a9fdd459#diff-4fe22885f772e47d3561a05348f73921669ec12d4413b220383b73c7ae484bc4R608-R610

### References

- https://jira.xwiki.org/browse/XWIKI-19752

### For more information
If you have any questions or comments about this advisory:

- Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
- Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-c5v8-2q4r-5w9v
- https://nvd.nist.gov/vuln/detail/CVE-2022-36098
- https://github.com/xwiki/xwiki-platform/commit/4032dc896857597efd169966dc9e2752a9fdd459#diff-4fe22885f772e47d3561a05348f73921669ec12d4413b220383b73c7ae484bc4R608-R610
- https://github.com/xwiki/xwiki-platform/commit/4f290d87a8355e967378a1ed6aee23a06ba162eb
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19752
