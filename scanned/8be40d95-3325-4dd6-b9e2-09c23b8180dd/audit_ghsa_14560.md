# [M] xwiki contains Incorrect Authorization

## Summary
Severity: Medium
Advisory: GHSA-859x-p6jp-rc2w
CVE: CVE-2023-26056
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-859x-p6jp-rc2w
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rendering-macro-context` — affected >=3.0-milestone-1 <13.10.10
- Maven: `org.xwiki.platform:xwiki-platform-rendering-macro-context` — affected >=14.0-rc-1 <14.4.5
- Maven: `org.xwiki.platform:xwiki-platform-rendering-macro-context` — affected >=14.5 <14.8-rc-1

## Details
### Impact

It's possible to execute a script with the right of another user (provided the target user does not have programming right).

For example, the following:

```
{{context document="xwiki:XWiki.userwithscriptright" transformationContext="document"}}{{velocity}}Hello from Velocity!{{/velocity}}{{/context}}
```

written by a user not having script right (for example in the user's profile) should produce an error (the user is not allowed to write scripts). However, because of the vulnerability, if the author of the document "xwiki:XWiki.userwithscriptright" has script right (but not programming right) the script will be executed with as if it was written by the target user.

### Patches

The problem has been patched in XWiki 14.8RC1, 14.4.5 and 13.10.10.

### Workarounds

There's no workaround for this issue.

### References

https://jira.xwiki.org/browse/XWIKI-19856

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [JIRA](https://jira.xwiki.org)
* Email us at [security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-859x-p6jp-rc2w
- https://nvd.nist.gov/vuln/detail/CVE-2023-26056
- https://github.com/xwiki/xwiki-platform/commit/4b75f212c2dd2dfc5fb5726c7830c6dbc9a425c6
- https://github.com/xwiki/xwiki-platform/commit/bd34ad6710ed72304304a3d5fec38b7cc050ef3b
- https://github.com/xwiki/xwiki-platform/commit/dd3f4735b41971b3afc3f3aedf6664b4e8be4894
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19856
