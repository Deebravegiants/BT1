# [M] NLTK: Uncontrolled resource consumption in RecursiveDescentParser via ambiguous or left-recursive grammars

## Summary
Severity: Medium
Advisory: GHSA-ff5c-cp5c-9wjf
CVE: CVE-2026-12876
CWE: CWE-407, CWE-674
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-ff5c-cp5c-9wjf
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.3

## Details
`nltk.parse.RecursiveDescentParser` (and `SteppingRecursiveDescentParser`) enumerate parses top-down with no bound on the number of recursive steps. A small, crafted context-free grammar makes a short input consume unbounded CPU (and/or exhaust the Python recursion stack), pinning a process indefinitely — a denial of service.

## Proof of concept

Both of the following hang on a 24-token input (killed after 8s; growth is super-linear in input length), on NLTK develop:

```python
from nltk import CFG
from nltk.parse import RecursiveDescentParser

# (a) left recursion -> unbounded recursion
g = CFG.fromstring("S -> S S | 'a'")
list(RecursiveDescentParser(g).parse(["a"] * 24))   # hangs

# (b) ambiguous grammar -> exponential number of parses
g = CFG.fromstring("S -> 'a' S | 'a' S S | 'a'")
list(RecursiveDescentParser(g).parse(["a"] * 24))   # hangs
```

## Impact

An application that runs `RecursiveDescentParser` on a grammar (or an input) drawn from an untrusted source can be driven into an unbounded CPU / stack-exhaustion loop by a tiny payload. No confidentiality or integrity impact; single-process availability only.

## Sibling

The RegexpTokenizer ReDoS reported alongside this (CVE-2026-12875) is a different class (caller-supplied regex) and is addressed under GHSA-w3v8-gmh9-3wv7.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-ff5c-cp5c-9wjf
- https://github.com/nltk/nltk/pull/3649
- https://github.com/nltk/nltk/commit/43aaca1b9024138421c97f970bf13ee19ac8129d
- https://github.com/nltk/nltk
- https://github.com/nltk/nltk/releases/tag/v3.10.3
