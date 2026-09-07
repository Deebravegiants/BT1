# [H] Plate: Media embed provider metadata can bypass URL sanitization and execute iframe JavaScript

## Summary
Severity: High
Advisory: GHSA-qj6x-xx2h-8hvv
CVE: CVE-2026-55596
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-qj6x-xx2h-8hvv
Type: github-advisory

## Affected
- npm: `@platejs/media` — affected >=53.0.0 <53.1.4

## Details
## Summary

The media embed renderer trusts serialized `provider` or `sourceUrl` metadata and skips the URL protocol validation that normally blocks unsafe media embed URLs. A crafted Plate document can set a known video provider while keeping `url` as a `javascript:` iframe source. When a victim opens that document in an app using the registry media embed component, the component renders the attacker URL directly as an iframe `src`.

## Impact

An attacker who can create or share Plate document content with another user can execute JavaScript in the victim browser context when the victim opens the document. This can expose application data available to the page and perform actions as the victim, depending on the host application's session model.

## Reproduction

Use a Plate editor or viewer that renders media embeds with the registry `MediaEmbedElement` and load a document containing this node:

```json
{
  "type": "media_embed",
  "provider": "vimeo",
  "sourceUrl": "https://vimeo.com/1",
  "url": "javascript:parent.postMessage('plate-media-xss','*')",
  "children": [{ "text": "" }]
}
```

When rendered, the node is treated as a Vimeo media embed because `provider` is present. The iframe receives the unvalidated `url` value as its `src`.

## Root Cause / Technical Details

`parseMediaUrl` is the intended hardening point for media embed URLs and rejects parser output unless the URL protocol is `http:` or `https:`. However, `useMediaState` had a fast path for serialized nodes that already contain `provider` or `sourceUrl`. That fast path returned `{ id, provider, sourceUrl, url }` directly and did not call `parseMediaUrl` or otherwise validate the stored `url`.

The registry `MediaEmbedElement` then checks that `embed.provider` is one of the video providers and renders non-YouTube video providers with `<iframe src={embed.url}>`. Because `provider` is attacker-controlled serialized document metadata, it can be set to `vimeo` while `url` remains `javascript:...`.

This is fixed in `@platejs/media` 53.1.4 by recomputing embed metadata from the render URL instead of trusting serialized `provider`, `id`, or `sourceUrl` metadata.

## PoC Evidence

A browser proof using the same data flow set an iframe `src` to:

```text
javascript:parent.postMessage('plate-media-xss','*')
```

Chromium executed the iframe JavaScript and the parent page received `plate-media-xss`, confirming execution from the iframe source.

## Remediation

Upgrade `@platejs/media` to 53.1.4 or later. Treat `provider`, `sourceUrl`, and `id` in serialized documents as untrusted derived metadata. Recompute embed metadata from `url` with `parseMediaUrl`, or at minimum validate any fast-path `url` with the same protocol allowlist before rendering an iframe.

## References
- https://github.com/udecode/plate/security/advisories/GHSA-qj6x-xx2h-8hvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-55596
- https://github.com/udecode/plate/pull/5014
- https://github.com/udecode/plate/commit/6214914ca811adf22d0ad503154494216eed68ba
- https://github.com/udecode/plate
- https://github.com/udecode/plate/releases/tag/v53.1.4
