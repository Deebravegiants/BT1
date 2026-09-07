# [H] league/commonmark: Denial of service via colliding heading slugs

## Summary
Severity: High
Advisory: GHSA-mh25-x5hq-wrqp
CWE: CWE-407
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-mh25-x5hq-wrqp
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=2.0.0 <2.9.0

## Details
### Impact

`UniqueSlugNormalizer::normalize()` makes each slug document-unique by searching for an unused numeric suffix, but **restarts that search from `1` on every collision**. The k-th heading that collapses to the same base slug performs k−1 array lookups, so K colliding slugs cost Σ(k−1) = **O(K²)**. An attacker can force every heading onto a single base slug trivially — many empty ATX headings, identical heading text, or punctuation-only headings that normalize to the empty string.

The path is reached whenever the shared slug normalizer runs over attacker-controlled text. That happens when `HeadingPermalinkExtension` is registered (its `HeadingPermalinkProcessor` normalizes every heading), independently through `FootnoteExtension` (its `AnonymousFootnoteRefParser` normalizes every `^[label]` reference), and on any `TableOfContentsExtension` site (which requires `HeadingPermalinkExtension` to be co-registered). The default `slug_normalizer/unique` setting (`UniqueSlugNormalizerInterface::PER_DOCUMENT`) accumulates collisions across the whole document. No authentication is required — a small document body turns into seconds of CPU and denies service. Availability impact only. **`UniqueSlugNormalizer` was introduced in 2.0.0 (first shipped in 2.0.0-beta1, May 2021); the 1.x heading-permalink slug generator performed no de-duplication and is not affected. All 2.x releases (including 2.8.x) are affected.**

### Workarounds

Integrators who cannot upgrade immediately can:

- **Set `slug_normalizer/unique` to `false` / `UniqueSlugNormalizerInterface::DISABLED`**, which stops the de-duplication scan entirely — at the cost of losing id uniqueness (colliding headings then share an anchor).
- **Disable `HeadingPermalinkExtension`** (and `TableOfContentsExtension`, which depends on it), and `FootnoteExtension` where anonymous footnotes reach the same normalizer, for untrusted Markdown.
- **Cap the accepted document size / heading count upstream** so K cannot reach the quadratic danger zone.

Each of these trades off functionality or correctness; upgrading to the patched release (which removes the quadratic behavior while keeping unique ids and identical output) is the recommended remediation.

## References
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-mh25-x5hq-wrqp
- https://github.com/thephpleague/commonmark
- https://github.com/thephpleague/commonmark/releases/tag/2.9.0
