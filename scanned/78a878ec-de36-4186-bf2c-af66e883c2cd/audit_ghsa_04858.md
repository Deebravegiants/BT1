# [M] UltraJSON: Malformed/Truncated UTF-8 Accepted and Silently Rewritten in ujson.dumps()

## Summary
Severity: Medium
Advisory: GHSA-3j69-69wj-xqx2
CVE: CVE-2026-54911
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-3j69-69wj-xqx2
Type: github-advisory

## Affected
- PyPI: `ujson` — affected >=0 <5.13.0

## Details
### Summary
`ujson.dumps()` (or `ujson.dump()` or `ujson.encode()`) have a `reject_bytes=False` option. When set, they may accept malformed or truncated UTF-8 byte sequences, silently rewriting them into different Unicode characters instead of rejecting them. This leads to input validation bypass and data integrity issues.

### Details

The expected behavior is that for `x` being any bytes string, `x == ujson.loads(ujson.dumps(x, reject_bytes=False)).encode(errors="surrogatepass")` should always either be true or `ujson.dumps()` will throw an exception. In reality, some strings which should've been errors are silently rewritten as other strings:

* Invalid continuation bytes are replaced with valid ones: `b'\xcf\x13'` -> `b'\xcf\x93'`
* Unterminated sequence completes the sequence: `b'\xc3'` -> `b'\xc3\x80'`
* ... or leads to reading past the end of string: `b'\xf0\x90\x94'` -> `b"\xf0\x90\x94\x80inxcontrib'"`

### Impact

An application relying on reject_bytes=False for UTF-8 handling may experience:

- Data integrity issues
- Experience validation bypass if said validation occurs before serialisation

### Remediation

The missing/broken UTF-8 validation checks were added/fixed in https://github.com/ultrajson/ultrajson/commit/169eaf36b1116fece5034ee79a7a0ef3f6deedcf. We recommend upgrading to [UltraJSON 5.13.0](https://github.com/ultrajson/ultrajson/releases/tag/5.13.0).

### Workarounds

Decoding bytes to strings in Python before passing them to `ujson.dumps()` avoids this issue.

## References
- https://github.com/ultrajson/ultrajson/security/advisories/GHSA-3j69-69wj-xqx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-54911
- https://github.com/ultrajson/ultrajson/commit/169eaf36b1116fece5034ee79a7a0ef3f6deedcf
- https://github.com/pypa/advisory-database/tree/main/vulns/ujson/PYSEC-2026-2294.yaml
- https://github.com/ultrajson/ultrajson
- https://github.com/ultrajson/ultrajson/releases/tag/5.13.0
