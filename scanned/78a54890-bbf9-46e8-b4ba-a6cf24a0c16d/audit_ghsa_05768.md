# [M] league/commonmark: Denial of service via deeply nested XML output

## Summary
Severity: Medium
Advisory: GHSA-mj63-m3rc-8ppr
CWE: CWE-405
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-mj63-m3rc-8ppr
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=2.0.0 <2.9.0

## Details
### Impact

`XmlRenderer` pretty-prints XML by emitting depth-proportional indentation whitespace for **every** opening and closing tag. For a tree of depth n, the indentation alone sums to **O(n²)** bytes of output (and corresponding memory), reachable through `MarkdownToXmlConverter` — e.g. `str_repeat('> ', $depth) . "x\n"`, a single line of nested blockquotes — or through a direct `XmlRenderer::renderDocument()` call on an attacker-influenced AST.

This affects applications that convert untrusted Markdown to XML, which is an **opt-in** output path. The parser's `max_nesting_level` bounds the depth of *parser-created* trees, but its default is high enough to reach damaging sizes, can be raised by the host application, and does not constrain custom or programmatically built ASTs handed straight to the renderer. The result is a memory / output-size amplification rather than a hard crash, which is why this issue is rated **Medium** rather than High. No confidentiality or integrity impact. XML rendering was introduced in 2.0.0 (first shipped in 2.0.0-beta1, June 2021) and has emitted depth-proportional indentation ever since, so all 2.x releases are affected (verified against 2.8.x, clean upstream `1902f60f`). 1.x has no XML renderer and is not affected.

### Workarounds

Applications converting untrusted Markdown to XML should:

- **Lower `max_nesting_level`** to a conservative value appropriate to expected content, so the parser refuses to build extremely deep trees. This is the most direct lever for parser-produced ASTs, but does not protect trees built programmatically and passed straight to `XmlRenderer`.
- **Cap input size before conversion**, since the amplification is driven by input-proportional depth.
- **Constrain XML consumers** with memory / output-size limits (and streaming or size caps on any downstream XML parser or storage) so one request cannot allocate unbounded output.
- **Prefer HTML rendering** for untrusted content where XML is not strictly required — the HTML renderer does not emit depth-proportional indentation and is not subject to this amplification.

## References
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-mj63-m3rc-8ppr
- https://github.com/thephpleague/commonmark/commit/b5ac8c3947ca81844e85a09c7e0a5b4148bde2e1
- https://github.com/thephpleague/commonmark
- https://github.com/thephpleague/commonmark/releases/tag/2.9.0
