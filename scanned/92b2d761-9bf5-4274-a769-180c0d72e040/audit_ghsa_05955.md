# [H] league/commonmark:  Denial of service via duplicate footnote definitions

## Summary
Severity: High
Advisory: GHSA-jfm3-95jq-q3rf
CWE: CWE-407
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-jfm3-95jq-q3rf
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=1.5.0 <2.9.0

## Details
### Impact

The Footnote extension records one backref per footnote *reference* and then appends the **entire** backref list for **every** footnote *definition* block in the document, without ever de-duplicating or removing repeated definitions of the same label (`GatherFootnotesListener`, populated by `NumberFootnotesListener`). A document that references a single label N times and also supplies N duplicate `[^a]:` definitions of that label therefore produces **N × N** `FootnoteBackref` nodes, so output size, parse time, and peak memory are all **O(N²)**.

Reaching the vulnerable path requires `FootnoteExtension` to be registered on the `Environment`. This is opt-in, but is a commonly enabled GFM-style feature; no other non-default configuration is required. An unauthenticated attacker can expand a **~10 KB** request into a **~62 MB** HTML response, **~3 s** of CPU, and **~440 MB** of peak memory — enough to OOM-kill a default 128 MB PHP worker and deny service. Availability impact only; no confidentiality or integrity effect. **The Footnote extension was introduced in 1.5.0 (May 2020) with this backref logic present from the first commit, so all releases from 1.5.0 onward (including every 2.x through 2.8.x) are affected.**

### Workarounds

There is no library-level option to cap the number of footnotes, references, or definitions, so no configuration switch prevents the amplification. Integrators who cannot upgrade should:

- **Disable the Footnote extension** for untrusted input, or
- **Enforce a strict input-size limit before conversion** — but note this is a weak control here, since the ~10 KB payload that already triggers the 62 MB / ~440 MB blowup is well within typical request-body limits, so any cap must be aggressively small to help.

Upgrading to the patched release is the recommended remediation.

## References
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-jfm3-95jq-q3rf
- https://github.com/thephpleague/commonmark/commit/66028124a17ba193da7b11cc3dfda92df21bfbf4
- https://github.com/thephpleague/commonmark
- https://github.com/thephpleague/commonmark/releases/tag/2.9.0
