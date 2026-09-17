# [H] discord-html not escaping HTML code blocks when lacking a language identifier

## Summary
Severity: High
Advisory: GHSA-9r27-994c-4xch
Ecosystem: npm
Published: 2020-02-24
Source: https://github.com/advisories/GHSA-9r27-994c-4xch
Type: github-advisory

## Affected
- npm: `discord-markdown` — affected >=0 <2.3.1

## Details
### Impact
Any website using discord-markdown with user-generated markdown is vulnerable to having code injected into the page where the markdown is displayed.

### Patches
This has been patched in version 2.3.1

### Workarounds
Escape the characters `&lt;&gt;&amp;` before sending plain code blocks to discord-markdown.

### References
https://github.com/brussell98/discord-markdown/issues/13

## References
- https://github.com/brussell98/discord-markdown/security/advisories/GHSA-9r27-994c-4xch
- https://github.com/brussell98/discord-markdown/issues/13
- https://github.com/brussell98/discord-markdown/commit/7ce2eb66520815dcf5e97ef2bc8a2d5979da66e7
