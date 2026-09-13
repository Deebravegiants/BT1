# [M] @astrojs/rss: XML Injection via Unescaped RSS Feed Fields

## Summary
Severity: Medium
Advisory: GHSA-8j5q-mfj2-5q9q
CVE: CVE-2026-59728
CWE: CWE-91
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-8j5q-mfj2-5q9q
Type: github-advisory

## Affected
- npm: `@astrojs/rss` — affected >=1.0.0 <4.0.19

## Details
## Summary

In `@astrojs/rss`, the `source.title` and `enclosure.type` item fields are interpolated directly into XML template strings without XML-character escaping before being parsed by `fast-xml-parser`. An attacker who controls these field values can inject arbitrary XML elements into the generated RSS feed.

## Details

Two fields in `packages/astro-rss/src/index.ts` are affected:

### `source.title`

```typescript
item.source = parser.parse(
  `<source url="${result.source.url}">${result.source.title}</source>`,
).source;
```

`source.title` is validated only as `z.string()`, with no restriction on XML special characters. A value containing `</source>` followed by arbitrary XML is parsed as real XML elements, merging injected nodes into the RSS item.

### `enclosure.type`

```typescript
item.enclosure = parser.parse(
  `<enclosure url="${enclosureURL}" length="${result.enclosure.length}" type="${result.enclosure.type}"/>`,
).enclosure;
```

`enclosure.type` is also `z.string()` and is interpolated into an XML attribute without escaping. A value containing `"` followed by additional XML can break out of the attribute and inject extra elements.

## Proof of Concept

`source.title` injection:

```javascript
source: {
  url: 'https://legit.example.com',
  title: '</source><item><title>INJECTED</title><link>https://evil.com</link></item><source>',
}
// Result: RSS feed contains an injected <item> element with an evil.com link
```

`enclosure.type` injection:

```javascript
enclosure: {
  url: 'https://example.com/a.mp3',
  length: 0,
  type: 'audio/mpeg" /><link>https://evil.example.com</link><enclosure fake="',
}
// Result: RSS feed contains an injected <link> element
```

Both injections were confirmed with `fast-xml-parser`: the injected `"link": "https://evil.com"` appears in the parsed output.

## Impact

An attacker who can control `source.title` or `enclosure.type` values (e.g., via a CMS, database, or user-submitted content that populates `RSSFeedItem`) can inject arbitrary XML into the generated RSS feed. This corrupts feed structure, injects false metadata (e.g., a fake `<link>` pointing to a malicious URL), and can cause feed readers to misparse or display attacker-controlled content. In SSR mode (`output: 'server'`), the poisoned feed is served on every request to all subscribers.

## Patches

Fixed in `@astrojs/rss@4.0.19`.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-8j5q-mfj2-5q9q
- https://nvd.nist.gov/vuln/detail/CVE-2026-59728
- https://github.com/withastro/astro/pull/17209
- https://github.com/withastro/astro/commit/fbcfa039dfe3d700b239f595a6c55ee35e45bd06
- https://github.com/withastro/astro
- https://github.com/withastro/astro/releases/tag/@astrojs/rss@4.0.19
