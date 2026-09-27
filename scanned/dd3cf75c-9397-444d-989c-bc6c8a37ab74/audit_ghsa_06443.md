# [M] NLTK: Quadratic CPU Exhaustion in `XMLCorpusView._read_xml_fragment()`

## Summary
Severity: Medium
Advisory: GHSA-vp2x-qp44-57v7
CVE: CVE-2026-81723
CWE: CWE-400, CWE-407
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-vp2x-qp44-57v7
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.3

## Details
## Summary

`XMLCorpusView._read_xml_fragment()` reads a corpus file in 1 KiB blocks, appending
each block to a growing `fragment` string, then calls `_VALID_XML_RE.match(fragment)`
on the full accumulated buffer every iteration. Because each iteration rescans the
entire accumulated fragment, the total amount of work grows quadratically with input
size.

Commit `c9c332284` (CWE-1333) made each `match()` call linear. The quadratic behavior
is separate: the loop calls `match()` once per 1 KiB block, each time on a longer
buffer.

On the test system, an 8 MiB malformed XML file consumed approximately 48 CPU-seconds
through the public `BNCCorpusReader.words()` API with no source modification. Absolute
timings vary by hardware. `_read_xml_fragment()` imposes no limit on fragment size or
iteration count.

## Details

**File:** `nltk/corpus/reader/xmldocs.py`  
**Function:** `XMLCorpusView._read_xml_fragment()`, lines 261–308

The relevant loop:

```python
fragment = ""
while True:
    fragment += stream.read(self._BLOCK_SIZE)      # grows by 1 KiB per iteration
    if self._VALID_XML_RE.match(fragment):         # rescans full buffer each time
        return fragment
    ...
    last_open_bracket = fragment.rfind("<")
    if last_open_bracket > 0:                      # False for single-'<' payload
        if self._VALID_XML_RE.match(fragment[:last_open_bracket]):
            return ...
    # loop continues
```

For a payload of `b'<' + b'a' * (N-1)`:

- For this malformed input, `_VALID_XML_RE.match(fragment)` does not succeed because
  the unterminated tag prevents the expression from matching before EOF.
- `fragment.rfind("<")` returns `0`; the guard `last_open_bracket > 0` is `False`, so
  the backtrack branch is never taken.
- The only exit is EOF, after all N bytes are consumed.

**Affected readers** -> readers that rely on `XMLCorpusView`, including
`BNCCorpusReader`, `NPSChatCorpusReader`, `SemcorCorpusReader`, `MTECorpusReader`,
`NKJPCorpusReader`, `FrameNetCorpusReader`, `VerbNetCorpusReader`, and direct
`XMLCorpusView` instantiation. `XMLCorpusReader.xml()` is not affected -> it calls
`defusedxml.safe_parse()`.

## PoC

Requires only `pip install nltk`. No corpus data needed.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from nltk.corpus.reader.bnc import BNCCorpusReader

SIZES_KIB = (256, 512, 1024, 2048, 4096, 8192)
results = []
with TemporaryDirectory() as directory:
    root = Path(directory)
    malformed = root / "unterminated.xml"
    for kib in SIZES_KIB:
        malformed.write_bytes(b"<" + b"a" * (kib * 1024 - 1))
        t = perf_counter()
        try:
            list(BNCCorpusReader(str(root), [malformed.name]).words())
        except ValueError as e:
            assert "tag not closed" in str(e)
        results.append(perf_counter() - t)

print("KiB      seconds   growth")
for i, (kib, elapsed) in enumerate(zip(SIZES_KIB, results)):
    ratio = "-" if i == 0 else f"{elapsed / results[i-1]:.2f}x"
    print(f"{kib:5d}  {elapsed:9.3f}  {ratio}")
```

Runtime should increase by approximately fourfold for each doubling of input size,
although absolute timings vary by hardware.

During verification, `_VALID_XML_RE.match()` was instrumented to record the size of
each input. For a 256 KiB malformed file it was invoked 257 times on monotonically
increasing buffers (1024, 2048, …, 262144 bytes), with the final call occurring after
EOF. This confirms that every iteration rescans the accumulated fragment.

## Impact

Applications that process attacker-controlled XML corpus files through an affected reader
are vulnerable. The attacker needs only write access to a path the reader will open. No
NLTK credentials or special privileges required. Offline tools reading only trusted
local corpora are not at risk.

**Affected versions:** Verified in NLTK 3.9.4, 3.10.0, and the current develop branch.
Historical inspection indicates the same loop structure has existed since the
introduction of `XMLCorpusView` (2007), but only the listed versions were
experimentally verified. No patch exists in any published release.

This issue results in CPU exhaustion and may allow denial of service in applications
that process attacker-controlled XML corpus files.

## Suggested Fix

Avoid rescanning the accumulated fragment from the beginning after each 1 KiB read.
Incremental parsing, bounded fragment accumulation, or another streaming approach would
eliminate the quadratic behavior while preserving existing semantics.

A regression test should verify that `BNCCorpusReader.words()` raises `ValueError`
within a fixed timeout (e.g. 5 seconds) against a 2 MiB malformed input. The existing
`test_xmldocs_security.py` covers only the prior ReDoS payloads and does not exercise
this path.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-vp2x-qp44-57v7
- https://nvd.nist.gov/vuln/detail/CVE-2026-81723
- https://github.com/nltk/nltk/commit/7808692d451b962711005d954859bb83aabcf8fa
- https://github.com/nltk/nltk
- https://github.com/nltk/nltk/releases/tag/v3.10.3
- https://www.vulncheck.com/advisories/nltk-before-3.10.3-quadratic-cpu-exhaustion-via-xmlcorpusview
