# [H] league/commonmark: Denial of service via crafted code fences, reference links, and emphasis delimiters

## Summary
Severity: High
Advisory: GHSA-j8pm-gj4c-rq4x
CWE: CWE-1050, CWE-1333, CWE-407
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-j8pm-gj4c-rq4x
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=0.6.0 <2.9.1

## Details
### Impact

Affected versions of `league/commonmark` perform super-linear work on three independent parsing paths, all of which are reachable on a stock `new CommonMarkConverter()` with default configuration and no extensions registered. Each trigger fits on a single line of input, so no complex Markdown structure is required.

The three paths were introduced at different times. This advisory's version range is their union; the individual ranges are:

| Path | Affected from | Affected through |
|---|---|---|
| 1. Fenced code block detection | `0.6.0` | `2.9.0` |
| 2. Reference link label lookup | `0.6.0` | `2.9.0` |
| 3. Emphasis / strikethrough delimiters (`*`, `_`, `~`) | `2.6.0` | `2.9.0` |
| 3. Highlight delimiters (`=`) | `2.9.0` | `2.9.0` |

**1. Fenced code block detection — quadratic, affected from 0.6.0.**

`FencedCodeStartParser` matches the following pattern:

```
/^[ \t]*(?:`{3,}(?!.*`)|~{3,})/
```

The lookahead enforces the CommonMark rule that a backtick fence's info string may not itself contain a backtick, but neither the lookahead nor the backtick run it guards is atomic or possessive. On a line consisting of a long backtick run, filler text, and a single trailing backtick, the quantifier gives back one character at a time and re-runs the lookahead across the remainder of the line on every candidate fence length.

A 320 KB single line takes roughly 27 seconds to convert. The identical payload with one `x` character prefixed — which fails the parser's own leading-character guard — takes 0.011 seconds. `preg_last_error()` returns `0` at every input size tested, including runs of 160,000 characters, so PCRE never reaches `pcre.backtrack_limit` and this is sustained CPU consumption rather than an early bail-out.

**2. Reference link label lookup — effectively quadratic, affected from 0.6.0.**

When a shortcut or collapsed reference link is attempted, `CloseBracketParser::tryParseReference()` copies the entire span between the brackets and passes it to `ReferenceMap::get()`, which normalizes the label — up to four full passes over its length (`trim`, `preg_replace`, `mb_check_encoding`, and `strtolower`, or `mb_convert_case` on the non-ASCII path). Nested brackets produce one such lookup per closing bracket, each on a span two characters longer than the last.

In 2.x the normalization sits behind an early return for an empty reference map, so a single 8-byte reference definition anywhere in the document (`[x]: y`) is enough to unlock the path. At n = 64,000 nested brackets the same input takes 22.0 seconds with that line present versus 0.59 seconds without it. A single non-ASCII character inside the brackets forces the `mb_convert_case` branch, costing roughly 2.5x more again.

**3. Emphasis, strikethrough, and highlight delimiter processing — super-linear, affected from 2.6.0.**

`DelimiterStack::processDelimiters()` remains linear only because of the `openersBottom` memo, which bounds the backward opener scan — an argument that holds only if the memo's key space is O(1). `EmphasisDelimiterProcessor::getCacheKey()`, and the equivalents in `StrikethroughDelimiterProcessor` and `MarkDelimiterProcessor`, embed the closer's raw current run length in the key, leaving that space unbounded. An attacker spends O(n) bytes minting a growing number of distinct run lengths; each distinct length is a fresh key whose recorded bound starts at zero, forcing a full backward re-scan of the entire pile of openers.

The resulting work grows as roughly n^1.5. This is sub-quadratic, but the amplification over linear growth itself scales with input size, so it worsens as inputs grow: 800 KB of ordinary asterisks, letters, and spaces costs roughly 27 seconds on a stock converter.

This path is a regression introduced in **2.6.0**. Before that release the cache key was the bare delimiter character — a bounded key space that amortized correctly. `*` and `_` are affected on any default configuration from 2.6.0 onward. `~` (`StrikethroughExtension`, included in `GithubFlavoredMarkdownConverter` and `GithubFlavoredMarkdownExtension`) is affected from 2.6.0. `=` (`HighlightExtension`) is affected only from **2.9.0**, when `MarkDelimiterProcessor` was declared cacheable.

**Overall impact.** An unauthenticated attacker who can submit Markdown for conversion can use a comparatively small request to consume disproportionate CPU time. Repeated or concurrent requests can occupy all available PHP workers and prevent legitimate requests from completing. The impact is limited to availability: no data is disclosed, rendered output is unchanged, and no rendering restriction is bypassed. Applications that process only trusted Markdown are not remotely exploitable.

Settings such as `html_input`, `allow_unsafe_links`, and `max_nesting_level` do not mitigate any of these, because the expensive work occurs during parsing, before rendering. `max_delimiters_per_line` bounds the third path only, and does so lossily — it silently discards emphasis once the cap is exhausted.

### Patches

The issues are patched in `2.9.1` and later:

- The fenced code block quantifier is now possessive, which is behavior-identical here: any character given back moves a backtick into the lookahead's scan range, so every retry was guaranteed to fail regardless.
- Reference link *lookups* now apply the CommonMark 999-character link label limit before copying and normalizing the label, matching the limit already enforced when parsing reference *definitions*. Because a definition can never exceed that length, an over-length lookup label cannot match one directly. One edge case does change: a label longer than 999 characters that *collapses* to a shorter match once whitespace is normalized — for example `[a` followed by 998 spaces and `b]` against a `[a b]: /url` definition — previously rendered as a link and now renders literally. This follows cmark, which applies its own label-length cap before normalizing (`cmark_reference_lookup()`), and matches how this library has always handled the equivalent `[text][label]` form via `LinkParserHelper::parseLinkLabel()`. commonmark.js normalizes first and still resolves such labels.
- Delimiter processor cache keys now clamp the run length to the coarsest bucket that can change behavior — `min(length, 2)` for emphasis, `min(length, 3)` for strikethrough and highlight — restoring a bounded key space while preserving byte-identical output.

Versions from `0.6.0` through `2.9.0` are affected by at least one of these paths; see the table above for which paths apply to which releases. The 0.x and 1.x release lines are no longer supported, so their users must upgrade to `2.9.1` or later.

### Workarounds

If you cannot upgrade immediately, enforce a **maximum length for individual lines** before passing input to the converter, in addition to a total request-size limit. A per-line limit matters because every trigger described above fits within a single line. Because the cost grows super-linearly, the cap must be genuinely small to bound worst-case CPU.

Setting `max_delimiters_per_line` reduces exposure to the delimiter path only, and does so by silently dropping emphasis from the rendered output. It has no effect on the fenced code or reference link paths.

Restricting conversion to trusted users, applying strict execution-time limits, rate-limiting requests, and limiting concurrent conversions all reduce exposure, but none is a complete substitute for upgrading.

## References
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-j8pm-gj4c-rq4x
- https://github.com/thephpleague/commonmark/commit/0768217751fbfaeb8d76762f6944e9af7114295e
- https://github.com/thephpleague/commonmark/commit/d9375fadc308a63a02950a68d822417a6e4c33b2
- https://github.com/thephpleague/commonmark/commit/e0036ef031fd36ec1c3c82db8743fc928b5271c8
- https://github.com/thephpleague/commonmark
- https://github.com/thephpleague/commonmark/releases/tag/2.9.1
