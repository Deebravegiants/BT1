# [H]  NLTK TweetTokenizer vulnerable to denial of service through catastrophic regex backtracking

## Summary
Severity: High
Advisory: GHSA-qx2g-xrx7-vfh8
CVE: CVE-2026-72818
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-qx2g-xrx7-vfh8
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.1

## Details
The URLS regular expression in nltk/tokenize/casual.py, compiled into TweetTokenizer.WORD_RE and applied by TweetTokenizer.tokenize, contains a naked-domain branch whose domain-label prefix [a-z0-9]+(?:[.\-][a-z0-9]+)* is unbounded. Input consisting of many alternating label separators can be partitioned in exponentially many ways, and because the branch also requires a trailing top-level domain that such input never supplies, the engine explores those partitions before failing at each offset. A few kilobytes of input therefore consumes seconds to minutes of single-threaded CPU, and the HANG_RE substitution performed before matching does not collapse the pattern. TweetTokenizer is intended for tokenizing untrusted social-media text, so any service that applies it, or the module-level casual_tokenize, to submitted text can be stalled per request without authentication. Version 3.10.1 bounds the label repetition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-72818
- https://github.com/nltk/nltk/issues/3704
- https://github.com/nltk/nltk/pull/3701
- https://github.com/nltk/nltk/commit/e092ed52eccae642304448bffc8d23cb301f85c1
- https://github.com/nltk/nltk
- https://github.com/nltk/nltk/blob/3.9.4/nltk/tokenize/casual.py
- https://github.com/nltk/nltk/releases/tag/v3.10.1
- https://www.vulncheck.com/advisories/nltk-tweettokenizer-url-pattern-backtracks-catastrophically-on-naked-domain-like-input
