# [H] league/commonmark: Denial of service via adjacent inline attribute blocks

## Summary
Severity: High
Advisory: GHSA-g2gp-3wwq-f4ph
CWE: CWE-407
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-g2gp-3wwq-f4ph
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=1.5.0 <2.9.0

## Details
### Impact

With the Attributes extension enabled, `AttributesListener::findTargetAndDirection()` resolves each attribute node's target by walking outward through its siblings. For a run of N adjacent inline attribute blocks placed at the start of a block (with nothing to their left), each node scans the **entire** sibling list to the far-right end before giving up and falling back to the parent. Each resolution is therefore Θ(N) and the whole run is **Θ(N²)**.

Reaching the path requires `AttributesExtension` (opt-in, but first-party: `League\CommonMark\Extension\Attributes\AttributesExtension`). No other configuration matters — the quadratic walk runs unconditionally during parsing and is **not** gated by the `attributes/allow` allow-list, the `on*` hardening added in 2.7.0, or `allow_unsafe_links`. An unauthenticated attacker can submit a **~32 KB** input (`{#a}` repeated 8,000 times) that takes **over 5 seconds** to convert, with time growing quadratically in input length — a cheap denial of service. Availability impact only. **The Attributes extension was introduced in 1.5.0 (May 2020) with this outward-walk resolver present from the first commit, so all releases from 1.5.0 onward (including every 2.x) are affected.**

### Workarounds

There is no library-level configuration that gates the quadratic walk. Integrators who cannot upgrade can only reduce exposure indirectly:

- **Disable the Attributes extension** for untrusted input, or
- **Impose a strict maximum input length before conversion** — noting that because the cost is quadratic, even a modest cap must be small to meaningfully bound worst-case CPU.

Upgrading to a release containing the fix is recommended.

## References
- https://github.com/thephpleague/commonmark/security/advisories/GHSA-g2gp-3wwq-f4ph
- https://github.com/thephpleague/commonmark/commit/2d4c0fafa62501be919262064cffa6d71687430b
- https://github.com/thephpleague/commonmark
- https://github.com/thephpleague/commonmark/releases/tag/2.9.0
