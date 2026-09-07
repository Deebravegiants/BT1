# [C] xwiki.platform:xwiki-platform-panels-ui Eval Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-c5f4-p5wv-2475
CVE: CVE-2023-29212
CWE: CWE-94, CWE-95
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-c5f4-p5wv-2475
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-panels-ui` — affected >=14.0-rc-1 <14.4.7
- Maven: `org.xwiki.platform:xwiki-platform-panels-ui` — affected >=14.5 <14.10

## Details
### Impact
Any user with edit rights can execute arbitrary Groovy, Python or Velocity code in XWiki leading to full access to the XWiki installation. The root cause is improper escaping of the included pages in the included documents edit panel.

A proof of concept exploit is to edit a document and add the following code before saving.

```
{{display reference="{{cache~}~}{{groovy~}~}println(~"Hello from Groovy~" + ~" in included document!~"){{/groovy~}~}{{/cache~}~}"/}}
```

**expected**
The right had side panels contain:
```
One included page: 
{{cache}}{{groovy}}println("Hello from Groovy" + " in included document!"){{/groovy}}{{/cache}}
```

**actual**
The right had side panels contain:
```
One included page:
    XWiki.Hello from Groovy in included document!
```

### Patches
The problem has been patched on XWiki 14.4.7, and 14.10.

### Workarounds
The issue can be fixed manually applying this [patch](https://github.com/xwiki/xwiki-platform/commit/22f249a0eb9f2a64214628217e812a994419b69f#diff-a51a252f0190274464027342b4e3eafc4ae32de4d9c17ef166e54fc5454c5689R214-R217).

### References
- https://github.com/xwiki/xwiki-platform/commit/22f249a0eb9f2a64214628217e812a994419b69f#diff-a51a252f0190274464027342b4e3eafc4ae32de4d9c17ef166e54fc5454c5689R214-R217
- https://jira.xwiki.org/browse/XWIKI-20293

### For more information
If you have any questions or comments about this advisory:

*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-c5f4-p5wv-2475
- https://nvd.nist.gov/vuln/detail/CVE-2023-29212
- https://github.com/xwiki/xwiki-platform/commit/22f249a0eb9f2a64214628217e812a994419b69f#diff-a51a252f0190274464027342b4e3eafc4ae32de4d9c17ef166e54fc5454c5689R214-R217
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20293
