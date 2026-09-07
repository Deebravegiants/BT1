# [M] Clipboard-based DOM-XSS

## Summary
Severity: Medium
Advisory: GHSA-gpfj-4j6g-c4w9
CVE: CVE-2021-37700
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-12
Source: https://github.com/advisories/GHSA-gpfj-4j6g-c4w9
Type: github-advisory

## Affected
- npm: `@github/paste-markdown` — affected >=0 <0.3.4

## Details
### Impact

A self Cross-Site Scripting vulnerability exists in the @github/paste-markdown library. If the clipboard data contains the string `<table>`, a **div** is dynamically created, and the clipboard content is copied into its **innerHTML** property without any sanitization, resulting in improper execution of JavaScript in the browser of the victim (the user who pasted the code). Users directed to copy text from a malicious website and paste it into pages that utilize this library are affected.

The following @github/paste-markdown code snippet is triggered when the user pastes something and the browser's clipboard data contains an entry whose content-type is **text/HTML**.

```typescript
function generateText(transfer: DataTransfer): string | undefined {
  if (Array.from(transfer.types).indexOf('text/html') === -1) return

  let html = transfer.getData('text/html')
  if (!/<table/i.test(html)) return

  html = html.replace(/<meta.*?>/, '')

  const el = document.createElement('div')
  el.innerHTML = html
  const tables = el.querySelectorAll('table')

  for (const table of tables) {
    if (table.closest('[data-paste-markdown-skip]')) {
      table.replaceWith(new Text(table.textContent || ''))
    }
    const formattedTable = tableMarkdown(table)
    table.replaceWith(new Text(formattedTable))
  }

  return el.innerHTML
}
```

### Patches
A security patch was released in [version 0.3.4](https://github.com/github/paste-markdown/releases/tag/v0.3.4).

### Workarounds
A Content Security Policy that prevents `unsafe-inline` helps reduce the likelihood of this vulnerability being exploited in modern browsers.

<!--
### References
_Are there any links users can visit to find out more?_

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [example link to repo](http://example.com)
* Email us at [example email address](mailto:example@example.com)
*
-->

## References
- https://github.com/github/paste-markdown/security/advisories/GHSA-gpfj-4j6g-c4w9
- https://nvd.nist.gov/vuln/detail/CVE-2021-37700
- https://github.com/github/paste-markdown/commit/32b7ea3f29ae8f256f9d19768387be42678ddf30
- https://github.com/github/paste-markdown
- https://github.com/github/paste-markdown/releases/tag/v0.3.4
- https://www.npmjs.com/package/@github/paste-markdown
