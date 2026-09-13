# [H] Mistune block_parser: quadratic-time parsing on long lists of repeated reference-link definitions

## Summary
Severity: High
Advisory: GHSA-ffq3-xpv3-j92q
CVE: CVE-2026-59928
CWE: CWE-1333, CWE-407
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-ffq3-xpv3-j92q
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <3.3.0

## Details
## Summary

**Type:** Algorithmic-complexity DoS in reference-link definition handling. A markdown document with N reference-link definitions of the same key (or many distinct keys) takes O(N²) parser time. 5000 repeated `[a]: u\n` definitions take ~1.1 second; 10000 → ~4.5 seconds.
**File:** `src/mistune/block_parser.py` (reference-link def parsing) and the surrounding `ref_links` env-dictionary handling.
**Root cause:** every reference definition is parsed by scanning forward from each candidate position. The `unikey` normalisation runs per-def, the dictionary insert is per-def, and the lookup-by-label-then-iterate-defs path is linear in the number of stored defs. For input with N defs, the total work is O(N²).

## Affected Code

`src/mistune/block_parser.py` — reference-definition rule fires on every line that matches `[label]: url`. For each one:
- `unikey(label)` is called (linear scan of the label).
- The def is appended to `state.env['ref_links']`.
- Later inline-link resolution looks up by `unikey(label)` in the dict (O(1)) but the surrounding parser revisits the def list for paragraph-vs-def disambiguation.

The cumulative parse time grows as the square of the number of defs.

**Why it's wrong:** the parser does not amortise the def-list scan. A single forward pass with a hash-keyed dict (already in place) plus a per-line classifier should make this O(N).

## Exploit Chain

1. Application uses mistune to render attacker-supplied markdown. No plugins required.
2. Attacker submits a 35 KB document of `[a]: u\n` repeated 5000 times followed by `[click][a]`.
3. CPU pegs for ~1.1 seconds. 10000 defs → ~4.5 s. 20000 → ~18 s. Doubling input quadruples time.

## Security Impact

**Attacker capability:** small input → large CPU. Predictable scaling. Can be repeated.
**Preconditions:** application uses `mistune.create_markdown()` (default config) on attacker-supplied markdown. Worth noting: the `ref_links` dictionary persists for the lifetime of the parse, so a long document with many defs builds up memory; with N defs of attacker-chosen length, the per-def normalisation cost compounds.
**Differential:** PoC-verified against mistune@3.2.1, default config:

```python
import mistune, time
md = mistune.create_markdown()
for n in [1000, 2000, 5000, 10000]:
    s = '[a]: u\n' * n + '[click][a]'
    t = time.time()
    md(s)
    print(f'  ref defs * {n} ({len(s)}b): {(time.time() - t) * 1000:.0f}ms')

# Output (Python 3.13, Linux, 2.5GHz CPU):
#   ref defs *  1000  ( 7012b):    46ms
#   ref defs *  2000 (14012b):   186ms
#   ref defs *  5000 (35012b):  1121ms
#   ref defs * 10000 (70012b):  4400ms
```

The patched build (with the surrounding parser amortised to O(N)) keeps the time linear.

## Suggested Fix

Replace the per-def re-scan with a single forward pass that classifies each line into `ref_def | paragraph | other` once and only inserts into `ref_links` once per def. The dict already exists; the wasted work is in the surrounding scan loop, not in the dict operations.

A regression test asserting that `md('[a]: u\n' * 50_000 + '[click][a]')` completes in under 1 second would catch any regression.

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-ffq3-xpv3-j92q
- https://nvd.nist.gov/vuln/detail/CVE-2026-59928
- https://github.com/lepture/mistune/commit/2b04d7ba341c16ac78fe82d3076bdd5c3de87c69
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/releases/tag/v3.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mistune/PYSEC-2026-2216.yaml
