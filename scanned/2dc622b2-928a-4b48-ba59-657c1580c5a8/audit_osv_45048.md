# [H] Cstruct indexing bugs can corrupt filtered output and reverse parsing results

## Summary
Severity: High
Advisory: OSEC-2026-20
Aliases: CVE-2026-89087
Ecosystem: opam
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/OSEC-2026-20
Type: osv

## Affected
- opam: `cstruct` — affected >=0 <6.3.0, >=0 <936f1010d3e9914da9c5c8a4739e9278a37e1c3e

## Details
Several functions in cstruct may use wrong data, leading to unexpected exceptions and return corrupted data.

## Impact

- `Cstruct.filter_map` writes retained bytes at their original input positions, producing corrupted output when earlier bytes are dropped.
- `Cstruct.tail ~rev:true` removes two bytes instead of one and raises an exception for single-byte views.
- `Cstruct.cuts ~rev:true` may compare input against the wrong data, split at incorrect positions, and construct results using offsets outside the requested view.
- `Cstruct.find` and `Cstruct.find_sub ~rev:true` may return slices from the wrong location when operating on non-zero-offset views.

These are a set of logical indexing and bounds-calculation errors (CWE-682), and not direct memory-safety vulnerabilities. However, affected operations may return corrupted data, raise an unexpected exception, split input incorrectly, or return bytes outside the requested Cstruct view but still within its backing buffer.

In security-sensitive parsers, this could cause validation bypasses, denial of service, or unintended disclosure of adjacent buffer contents.

## Workarounds

Users unable to upgrade cstruct should backport the corresponding source changes. There is no configuration-based mitigation since these are buggy library calls.

## References

Discovered via [Scrutineer](https://github.com/alpha-omega-security/scrutineer) and Deepseek GLM-5.3 Flash running locally.

## Timeline

- 2026-09-04: reported via GitHub to ocaml/security-advisories repository
- 2026-09-05: reported via email to security@ocaml.org
- 2026-09-05: patch proposed and reviewed
- 2026-09-05: release cstruct 6.3.0
- 2026-09-10: published advisory

## References
- https://github.com/mirage/ocaml-cstruct/pull/324
