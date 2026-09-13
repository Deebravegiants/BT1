# [H] league/commonmark: Denial of service in the SmartPunct and Attributes extensions

## Summary
Severity: High
Advisory: GHSA-jjv6-8j6v-6j52
CWE: CWE-1050, CWE-407
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-jjv6-8j6v-6j52
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=1.5.0 <2.9.1

## Details
### Impact

Two first-party extensions contain quadratic parsing paths. Both ship with the library but must be explicitly registered on the `Environment`; neither is included in `CommonMarkConverter`, `GithubFlavoredMarkdownConverter`, or `GithubFlavoredMarkdownExtension`. **Applications that do not register `SmartPunctExtension` or `AttributesExtension` are not affected by this advisory.**

**1. `SmartPunctExtension` — quote replacement recopies the whole text node (affected from 2.0.0).**

`ReplaceUnpairedQuotesListener` converts each unpaired `Quote` node back to a `Text` node and merges it into its neighbours via `AdjacentTextMerger`. The merge reads the left node's literal into a local variable, appends to that variable, and writes it back — and because the read aliases the node's string, every append copies the entire accumulated literal rather than only the bytes added. The listener runs this once per surviving unpaired quote against the same continuously growing text node, so the same buffer is fully re-copied a linear number of times.

A 1.2 MB document of alternating text segments and apostrophes takes 34.9 seconds to convert, against 0.069 seconds for the same input with the extension not registered.

Hardened configuration makes this *worse* rather than better: `QuoteParser` appends the `Quote` node to the AST before pushing it onto the delimiter stack, so `max_delimiters_per_line` removes the quote-pairing work while leaving every node the listener must process.

**2. `AttributesExtension` — block-level attribute runs re-scan their siblings (affected from 1.5.0).**

`AttributesListener::findTargetAndDirection()` walks the entire remaining sibling chain for every block-level `Attributes` node whose target is the following node. The backward half of that walk returns immediately for such nodes, and the forward half stops only at a sibling that is not itself an attributes node — which a contiguous run never provides — so a run of k nodes costs k(k-1)/2 steps.

An input placing each `{#a}` on its own line, with a single reference definition to keep the run contiguous, takes 28.4 seconds at 16,000 attribute blocks while producing **zero bytes of output**.

This is the block-level counterpart of GHSA-g2gp-3wwq-f4ph, patched in 2.9.0. **That fix is incomplete:** the early break it introduced is guarded on the node being an `AttributesInline`, so block-level `Attributes` nodes still re-scan. Applications that upgraded to 2.9.0 specifically to address GHSA-g2gp-3wwq-f4ph remain exposed to this variant.

**3. `AttributesExtension` — class lists are rebuilt on every merge (affected from 1.5.0).**

`AttributesHelper::mergeAttributes()` round-trips the accumulated class list through `explode` and `implode` on each merge. An `#id` attribute assigns a scalar and skips the branch entirely, but a `.class` attribute appends to an array which is then imploded to a string, written to the target node, and read back on the next iteration — so the *i*th merge pays a cost proportional to *i* three separate times.

`{.c}` repeated 32,000 times takes 33.5 seconds, against 0.26 seconds for byte-identical input using `{#a}` — a 130x gap that widens with input size. Both the inline and the block-level attribute paths are affected.

**Overall impact.** An unauthenticated attacker who can submit Markdown to an affected application can consume disproportionate CPU time with a comparatively small request, occupying PHP workers and preventing legitimate requests from completing. The impact is limited to availability: no data is disclosed, rendered output is unchanged, and no rendering restriction is bypassed.

No library-level configuration gates any of these paths. For the Attributes extension in particular, neither the `attributes/allow` allow-list nor the `on*` event-handler hardening added in 2.7.0 has any effect, because the expensive work happens while parsing and resolving the AST, before any attribute filtering or rendering takes place.

### Patches

The issues are patched in `2.9.1` and later:

- Adjacent text merging now appends in place instead of reading, modifying, and writing back the whole literal, so a merge costs only the bytes added. This fixes the defect for every caller, not only the SmartPunct listener.
- `AttributesListener` now records the runs it has already walked, so each contiguous run of block-level attribute nodes is scanned once rather than once per node.
- Accumulated class lists no longer pass through `mergeAttributes()` repeatedly; the listener holds pending attributes and joins them in a single pass.

The SmartPunct path affects `2.0.0` through `2.9.0`. The Attributes paths affect `1.5.0` through `2.9.0`, including releases that already contain the 2.9.0 fix for GHSA-g2gp-3wwq-f4ph. The 1.x release line is no longer supported, so its users must upgrade to `2.9.1` or later.

### Workarounds

If you cannot upgrade immediately:

- **Do not register `SmartPunctExtension` or `AttributesExtension`** when converting untrusted Markdown. This fully removes the affected paths.
- If either extension is required, **impose a strict maximum input length before conversion**. Because the cost is quadratic, even a modest cap must be small to meaningfully bound worst-case CPU time.

Restricting conversion to trusted users, applying strict execution-time limits, and rate-limiting requests reduce exposure but are not substitutes for upgrading. Configuration options including `attributes/allow`, `max_delimiters_per_line`, `max_nesting_level`, `html_input`, and `allow_unsafe_links` do not mitigate these issues.

## References
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-jjv6-8j6v-6j52
- https://github.com/thephpleague/commonmark/commit/04a5d11ef6bf2d0b927310810d6a2a85d3c184b9
- https://github.com/thephpleague/commonmark/commit/2f611b599c51661b005dc45c16ceaa547546e687
- https://github.com/thephpleague/commonmark
- https://github.com/thephpleague/commonmark/releases/tag/2.9.1
