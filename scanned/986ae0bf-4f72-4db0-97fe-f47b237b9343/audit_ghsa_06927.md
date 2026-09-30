# [H] vLLM: ReDoS via structured_outputs.regex compiled without timeout in xgrammar and outlines backends

## Summary
Severity: High
Advisory: GHSA-rwxx-mrjm-wc2m
CVE: CVE-2026-55574
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-rwxx-mrjm-wc2m
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0 <0.24.0

## Details
## Summary

The `structured_outputs.regex` API parameter passes a user-supplied regex string directly to grammar compiler backends with no compilation timeout. In the xgrammar backend, the string reaches `compile_regex()` with no guard. In the outlines backend, `validate_regex_is_buildable()` blocks structural issues (lookarounds, backreferences) but provides zero protection against exponential DFA state-space explosion. Patterns like `(a+)+b` pass all checks and hang the inference worker.

## Root Cause

`backend_xgrammar.py:91` — no timeout:
```python
ctx = self.compiler.compile_regex(grammar_spec)
```

`backend_outlines.py:299–330` — structural checks only, no complexity analysis:
```python
def validate_regex_is_buildable(regex: str) -> None:
    sre_parse.parse(regex)   # AST parse only — does not detect exponential patterns
    _check_unsupported(...)  # blocks lookarounds/backrefs, not nested quantifiers
```

`backend_outlines.py:64` — no timeout:
```python
oc.Index(regex_string, vocabulary.inner)
```

## Impact

Denial of service — one request with an adversarial regex pattern hangs an inference worker indefinitely.

## Remediation

Wrap `compile_regex()` and `oc.Index()` calls in a thread with a deadline (e.g., 5 seconds). Add complexity analysis to `validate_regex_is_buildable()` to detect nested quantifier patterns before compilation.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-rwxx-mrjm-wc2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-55574
- https://github.com/vllm-project/vllm/pull/45118
- https://github.com/vllm-project/vllm/commit/2b3006076c5e9bc4cda9e03e3641388de3c5c286
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2304.yaml
- https://github.com/vllm-project/vllm
