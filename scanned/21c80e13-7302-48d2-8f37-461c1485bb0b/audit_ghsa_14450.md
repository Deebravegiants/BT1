# [M] xwiki vulnerable to Improper Handling of Exceptional Conditions

## Summary
Severity: Medium
Advisory: GHSA-52vf-hvv3-98h7
CVE: CVE-2023-26479
CWE: CWE-755
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-52vf-hvv3-98h7
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rendering-parser` — affected >=6.0 <13.10.10
- Maven: `org.xwiki.platform:xwiki-platform-rendering-parser` — affected >=14.0 <14.4.6
- Maven: `org.xwiki.platform:xwiki-platform-rendering-parser` — affected >=14.5 <14.9-rc-1

## Details
### Impact
Users with write rights can insert well-formed content that is not handled well by the parser. For instance, with `xwiki/2.1`, inserting a deeply nested group blocks (`((( ((( ((( ((( .... ))) ))) ))) )))` (see the generator below to produce a large payload) can lead to the parser throwing a `StackOverflowError`.
As a consequence, some pages becomes unusable, including:
- the user index (if the page containing the faulty content is a user page)
- the page index

Note that on the page, the normal UI is completely missing and it is not possible to open the editor directly to revert the change as the stack overflow is already triggered while getting the title of the document. This means that it is quite difficult to remove this content once inserted.

### Patches
This has been patched on XWiki 13.10.10, 14.4.6, and 14.9-rc-1.

### Workarounds
A temporary solution to avoid Stack Overflow errors is to increase the memory allocated to the stack by using the `-Xss` JVM parameter (e.g., `-Xss32m`). This should allow the parser to pass and to fix the faulty content.
Note that we did not evaluated the consequence on other aspects of the system (e.g., performances), and should be only be used as a temporary solution.
Also, this does not prevent the issue to occur again with another content.
Consequently, it is strongly advised to upgrade to a version where the issue has been patched.

### References
- https://jira.xwiki.org/browse/XWIKI-19838

### For more information
If you have any questions or comments about this advisory:
- Open an issue in [Jira](http://jira.xwiki.org/)
- Email us at [Security ML](mailto:security@xwiki.org)

### Payload Generator

The Javascript code below produces 32768 nested group blocks, around the `Hello` text.

```javascript
let result = "(((\nHello\n)))";
for (let i = 0; i < 15; ++i) {
  result = result.replace("Hello", result);
}
console.log(result);
```

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-52vf-hvv3-98h7
- https://nvd.nist.gov/vuln/detail/CVE-2023-26479
- https://github.com/xwiki/xwiki-platform/commit/e5b82cd98072464196a468b8f7fe6396dce142a7
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19838
