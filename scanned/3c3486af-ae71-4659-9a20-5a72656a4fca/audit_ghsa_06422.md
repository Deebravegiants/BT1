# [M] NLTK: Quadratic-time DoS in PorterStemmer via long runs of 'y'

## Summary
Severity: Medium
Advisory: GHSA-ww6m-cw3f-q94g
CVE: CVE-2026-81722
CWE: CWE-407
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-ww6m-cw3f-q94g
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.3

## Details
`nltk.stem.PorterStemmer.stem()` -- a ubiquitous public API applied to arbitrary, often untrusted, tokens -- runs in O(n^2) time on a token containing a long run of the letter 'y', letting a single ~20-50 KB token pin a CPU core (CWE-407).

## Root cause

`_is_consonant(word, i)` was made *iterative* (commit for #3633, GHSA/CWE-674) to fix an earlier unbounded-recursion `RecursionError` on `'y'*10000`. The iterative form walks *backward* over the whole run of 'y's on every call:

```python
while i > 0 and word[i] == 'y':
    negate = not negate
    i -= 1
```

`_measure()` then calls `_is_consonant(stem, i)` once for **every** position `i` of the stem. For a run of n 'y's that is sum_{i} O(i) = O(n^2). The recursion fix therefore traded a CWE-674 RecursionError for a CWE-407 quadratic-time DoS.

## Proof of concept

Measured (Python 3.13): `stem('y'*5000 + 'ness')` = 2.6s, `stem('y'*10000 + 'ness')` = 11.3s (2x input -> ~4.3x time = quadratic), `stem('y'*20000 + 'ness')` > 20s. A pure run of 'y' with no matching suffix is fast because the stemmer rules that call `_measure` do not fire; a real suffix such as 'ness' triggers `_measure` on the long stem.

```python
from nltk.stem import PorterStemmer
PorterStemmer().stem('y' * 20000 + 'ness')   # >20s of CPU
```

## Impact

Stemming is routinely applied to untrusted text (search, indexing, NLP pipelines). A single unbroken ~20-50 KB token of 'y' characters (no whitespace, so it survives tokenization) causes multi-second-to-minutes CPU consumption per request. No confidentiality/integrity impact; single-process availability only.

## Fix direction

Classify each character's consonant/vowel status in a single left-to-right O(n) pass (memoise the 'y' run parity) instead of re-walking the run on every `_is_consonant` call, so `_measure` and stemming are linear. This is a sibling of the corpus-reader quadratic advisories GHSA-vp2x-qp44-57v7 and GHSA-8mpw-7fpc-4gqj (CWE-407).

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-ww6m-cw3f-q94g
- https://nvd.nist.gov/vuln/detail/CVE-2026-81722
- https://github.com/nltk/nltk/commit/7808692d451b962711005d954859bb83aabcf8fa
- https://github.com/nltk/nltk
- https://github.com/nltk/nltk/releases/tag/v3.10.3
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2026-3738.yaml
- https://www.vulncheck.com/advisories/nltk-porterstemmer-before-3.10.3-quadratic-time-dos
