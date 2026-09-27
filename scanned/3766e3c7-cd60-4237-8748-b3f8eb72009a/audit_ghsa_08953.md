# [M] go-ipld-prime's DAG-CBOR and DAG-JSON decoders have unbounded recursion depth

## Summary
Severity: Medium
Advisory: GHSA-w239-58x2-q8p5
CVE: CVE-2026-42328
CWE: CWE-674
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-w239-58x2-q8p5
Type: github-advisory

## Affected
- Go: `github.com/ipld/go-ipld-prime` — affected >=0 <0.23.0

## Details
The DAG-CBOR and DAG-JSON decoders recurse on each nested map or list without a depth limit. A payload containing deeply nested collections causes the decoder to recurse once per level, growing the goroutine stack until the Go runtime terminates the process with a fatal stack overflow (distinct from a recoverable panic).

For DAG-CBOR, a payload of approximately 2 MB, consisting of repeated `0x81` (array-of-1) bytes followed by a terminator, produces around 2 million recursion frames and reliably exhausts Go's default 1 GB goroutine stack. The existing allocation budget does not prevent this: each nested collection header costs only a handful of budget units, so the stack is exhausted before the budget is. DAG-JSON has equivalent exposure via `[[[...]]]`-style payloads; it has no budget system and is therefore unprotected against recursion depth as well.

Schema-free decoding (using `basicnode.Prototype.Any`) allows arbitrary nesting depth. Schema-bound decoding bounds nesting only when the schema itself is non-recursive and contains no fields typed as `Any`; schemas with recursive type references or any `Any`-typed fields permit unconstrained nesting at those points.

The fix adds a configurable `MaxDepth` option to both decoders, defaulting to 1024 nested levels. The decoder returns `ErrDecodeDepthExceeded` when a payload nests beyond the limit. Well-formed IPLD data rarely approaches this depth in practice; the default is generous for legitimate use while preventing stack exhaustion.

## References
- https://github.com/ipld/go-ipld-prime/security/advisories/GHSA-w239-58x2-q8p5
- https://nvd.nist.gov/vuln/detail/CVE-2026-42328
- https://github.com/ipld/go-ipld-prime
