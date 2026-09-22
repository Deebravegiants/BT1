# [M] ciguard: SCA HTTP client reads response body without size cap

## Summary
Severity: Medium
Advisory: GHSA-xw8c-rrvx-f7xq
CVE: CVE-2026-44219
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-xw8c-rrvx-f7xq
Type: github-advisory

## Affected
- PyPI: `ciguard` — affected >=0.6.0 <0.8.2

## Details
## Summary

Both SCA HTTP clients (`src/ciguard/analyzer/sca/osv.py` and `src/ciguard/analyzer/sca/endoflife.py`) call `payload = json.loads(resp.read().decode('utf-8'))` without a maximum-bytes cap. A hostile or compromised endoflife.date / OSV.dev (or a successful TLS MITM) could return a multi-GB response, exhausting the ciguard process's memory.

## Threat scenario

ciguard process memory exhaustion → OOM kill or system swap thrash. Realistic when ciguard runs in CI with a limited memory budget (typical: 4-8 GB). No data integrity or confidentiality impact.

**Realism caveat:** both URLs are hardcoded HTTPS, so this is a low-realism threat (HTTPS prevents MITM unless the attacker controls a trusted CA or hijacks DNS in a way that doesn't trigger cert validation). The unbounded read is structural defence-in-depth, not a directly exploitable bug today.

## Patch

- New `MAX_RESPONSE_BYTES = 5 * 1024 * 1024` (5 MB) constant in both modules.
- `body = resp.read(MAX_RESPONSE_BYTES + 1)` with overflow check returns `None` (caller falls back to stale cache).
- 3 regression tests in `tests/test_sca_rules.py::TestSCAResponseSizeCap`.

## Discovery

Found during ciguard's first self-conducted pentest cycle, 2026-04-26.

## CVSS Scoring

- CVSS v3.1: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L` — 3.7 (Low)
- CVSS v4.0: `CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N` — first.org calc 3.1 (Low); GitHub's calc 6.3 (Medium). Vector is correct — choosing v3.1 as the structured score keeps the consistent Low rating across consumers.

## Reproduction

Monkey-patch `urllib.request.urlopen` to return a fake 50 MB response; observe memory growth before/after the call. Pre-fix: process memory grows by ~50 MB. Post-fix: `_fetch` returns `None`, memory growth bounded to MAX_RESPONSE_BYTES.

## References

- Fix released in [v0.8.2](https://github.com/Jo-Jo98/ciguard/releases/tag/v0.8.2)
- CI regression gate added in [v0.8.3](https://github.com/Jo-Jo98/ciguard/releases/tag/v0.8.3)
- https://www.cve.org/CVERecord?id=CVE-2026-44219

## References
- https://github.com/Jo-Jo98/ciguard/security/advisories/GHSA-xw8c-rrvx-f7xq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44219
- https://github.com/Jo-Jo98/ciguard
- https://github.com/Jo-Jo98/ciguard/releases/tag/v0.8.2
- https://github.com/Jo-Jo98/ciguard/releases/tag/v0.8.3
