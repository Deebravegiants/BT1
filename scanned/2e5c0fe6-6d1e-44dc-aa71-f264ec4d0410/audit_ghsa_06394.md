# [H] league/commonmark: Denial of service via distinctly-named attributes in the Attributes extension

## Summary
Severity: High
Advisory: GHSA-8rr7-cvq3-gmfh
CWE: CWE-1050, CWE-407
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-8rr7-cvq3-gmfh
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=1.5.0 <2.10.0

## Details
### Impact

`AttributesExtension` ships with the library but must be explicitly registered on the `Environment`; it is not included in `CommonMarkConverter`, `GithubFlavoredMarkdownConverter`, or `GithubFlavoredMarkdownExtension`. **Applications that do not register `AttributesExtension` are not affected by this advisory.**

Two paths in the extension re-process every attribute a node has already collected each time another attribute is applied to it. When the attributes carry distinct names, the collected set grows by one on every step and is walked again in full, so a run of *n* attributes costs O(n²).

**1. Attribute nodes resolving to a common target (affected from 1.5.0).**

`AttributesListener::processDocument()` merges each attribute node into the set accumulated for its target, then filters the result. Both operations traverse that entire set: `AttributesHelper::mergeAttributes()` rebuilds it with `array_merge()`, and `AttributesHelper::filterAttributes()` matches a regular expression against every name in it. A run of attribute nodes sharing one target therefore re-walks a set that grows by a key per node.

Two input shapes reach this path: adjacent inline attributes at the start of a block (`{a0="v"}{a1="v"}…`, where quoting the values is what keeps them separate — an unquoted value swallows the `}{` that follows it), and a chain of attribute blocks held at their default target by reference definitions (`{a0=v}` / `[a]: u` / `{a1=v}` / `[a]: u` / …).

256 KB of adjacent inline attributes takes 20.0 seconds to convert, against 0.09 seconds once patched.

**2. Consecutive attribute-block lines (affected from 2.0.0).**

`AttributesBlockContinueParser::tryContinue()` merges each continuation line into the block's accumulated attributes, again rebuilding the whole set on every line. One distinct attribute per line (`{a0=v}` / `{a1=v}` / …) grows it by a key each time.

256 KB of such lines takes 1.9 seconds to convert while producing **zero bytes of output**, against 0.08 seconds once patched.

**Relationship to GHSA-jjv6-8j6v-6j52.** The fix released in 2.9.1 for that advisory made the `class` attribute cheap to accumulate, but left every other attribute name on the original path. **Applications that upgraded to 2.9.1 or 2.9.2 remain exposed to this variant.**

**Overall impact.** An unauthenticated attacker who can submit Markdown to an affected application can consume disproportionate CPU time with a comparatively small request, occupying PHP workers and preventing legitimate requests from completing. The impact is limited to availability: no data is disclosed, rendered output is unchanged, and no rendering restriction is bypassed.

### Patches

The issue is patched in `2.10.0`. Both paths now fold each node — or each line — into the accumulated attributes at a cost proportional to that node or line alone, rather than re-merging and re-filtering everything gathered so far. Rendered output is unchanged, down to the order in which attributes appear.

The listener path affects `1.5.0` through `2.9.2`. The continuation-line path affects `2.0.0` through `2.9.2`. The 1.x release line is no longer supported, so its users must upgrade to `2.10.0` or later.

### Workarounds

If you cannot upgrade immediately:

- **Do not register `AttributesExtension`** when converting untrusted Markdown. This fully removes both paths.
- If the extension is required, **impose a strict maximum input length before conversion**. Because the cost is quadratic, the cap must be small to meaningfully bound worst-case CPU time.

The `attributes/allow` allow-list added in 2.7.0 is **not** a mitigation. A non-empty allow-list happens to bound the first path, because unlisted names are discarded before they accumulate, but it does nothing for the second: continuation lines are merged while parsing, before any filtering takes place.

Restricting conversion to trusted users, applying strict execution-time limits, and rate-limiting requests reduce exposure but are not substitutes for upgrading.

## References
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-8rr7-cvq3-gmfh
- https://github.com/thephpleague/commonmark/commit/f27eb720972490b5af4dbb635ad8634529faf9f2
- https://github.com/thephpleague/commonmark
- https://github.com/thephpleague/commonmark/releases/tag/2.10.0
