# [M] Hugo: XSS via text/html content files

## Summary
Severity: Medium
Advisory: GHSA-c54g-xjwj-8g82
CVE: CVE-2026-50133
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-c54g-xjwj-8g82
Type: github-advisory

## Affected
- Go: `github.com/gohugoio/hugo` — affected >=0 <0.162.0

## Details
**Commit:** [e41a06447d](https://github.com/gohugoio/hugo/commit/e41a06447d) — _Disallow HTML content by default_
**Affected versions:** all Hugo versions prior to v0.162.0.
**Fixed in:** v0.162.0.
**Severity:** Low to Medium, depending on threat model. Not an issue if you fully trust every file under `/content` and every content adapter you load.

**Description.** Hugo accepts content files in several markup formats. Files mapped to the `text/html` media type (typically `.html` files under `/content`, or pages produced by a content adapter that sets `content.mediaType = "text/html"`) had their body emitted verbatim into the rendered page. A site that ingests HTML content from an untrusted source — for example, a CMS-backed editor, a content adapter pulling from an external API, or an automated import pipeline — could therefore be served stored cross-site scripting.

**Mitigation.** v0.162.0 introduces a `security.allowContent` whitelist with `text/html` denied by default. Sites that intentionally author HTML content can opt back in:

```toml
[security]
allowContent = ['.*']
```

This only affects pages whose source file (or content adapter output) declares an HTML media type; Markdown, AsciiDoc, Org, Pandoc and reStructuredText content is unaffected.

## References
- https://github.com/gohugoio/hugo/security/advisories/GHSA-c54g-xjwj-8g82
- https://github.com/gohugoio/hugo/commit/e41a06447daa3071a01f333fdcec0a5153c3c8d1
- https://github.com/gohugoio/hugo
- https://github.com/gohugoio/hugo/releases/tag/v0.162.0
