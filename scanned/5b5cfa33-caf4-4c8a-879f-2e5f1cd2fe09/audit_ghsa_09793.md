# [M] go-ipld-prime: DAG-CBOR decoder unbounded memory allocation from CBOR headers

## Summary
Severity: Medium
Advisory: GHSA-378j-3jfj-8r9f
CVE: CVE-2026-35480
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-378j-3jfj-8r9f
Type: github-advisory

## Affected
- Go: `github.com/ipld/go-ipld-prime` — affected >=0 <0.22.0

## Details
The DAG-CBOR decoder uses collection sizes declared in CBOR headers as Go preallocation hints for maps and lists. The decoder does not cap these size hints or account for their cost in its allocation budget, allowing small payloads to cause excessive memory allocation.

A CBOR map or list header can declare an arbitrarily large number of entries, causing the decoder to preallocate proportionally large backing structures before any entries are actually read. Because the allocation budget is only decremented as entries are decoded (not when sizes are declared), this cost is effectively invisible to the budget system. This is compounded by nesting: each level of a nested structure triggers its own unchecked preallocation while consuming minimal budget (one entry per parent level), so a payload under 100 bytes with 10 levels of nesting can cause over 9GB of allocation.

Schema-free decoding (i.e. using `basicnode.Prototype.Any`) allows arbitrary nesting depth. Schema-bound decoding limits nesting to the schema's structure, but any field typed as `Any` in the schema permits unconstrained nesting within that field.

The fix caps the preallocation size hint to 1024 entries and decrements the allocation budget when collection sizes are declared. The declared length is still used for entry-count validation, and collections grow dynamically as entries are decoded, so correctly-formed data is unaffected, even beyond the preallocation limit.

## References
- https://github.com/ipld/go-ipld-prime/security/advisories/GHSA-378j-3jfj-8r9f
- https://nvd.nist.gov/vuln/detail/CVE-2026-35480
- https://github.com/ipld/go-ipld-prime/commit/e43bf4a27055fe8d895671a731ee5041e2d983a9
- https://github.com/ipld/go-ipld-prime
- https://github.com/ipld/go-ipld-prime/releases/tag/v0.22.0
