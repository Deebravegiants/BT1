# [M] Rocq Prover through 9.2.0 Guard Checker Trusts Corrupted Recursive Tree After Transport

## Summary
Severity: Medium
Advisory: CVE-2026-72704
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-72704
Type: osv

## Details
The guard checker in Rocq Prover does not recheck the recursive tree representation of an inductive type parameter after that parameter has been changed by transport. A fixpoint may apply a rewrite along an equality between types to its recursive argument, which the guard checker accepts because the inductive type is preserved, while the recursive tree recorded for the parameter is altered. A second fixpoint that calls the first inherits the altered recursive tree without verification, so a call that is not structurally decreasing is accepted as terminating. The resulting non-terminating definition proves that a natural number equals its own successor and therefore False, from which any proposition follows. The demonstration uses two axioms that follow from univalence and are consistent with the calculus of inductive constructions, so the contradiction comes from the guard check rather than from the assumptions. A fix is proposed but not merged.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72704.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72704
- https://www.vulncheck.com/advisories/rocq-prover-through-guard-checker-trusts-corrupted-recursive-tree-after-transport
- https://github.com/rocq-prover/rocq/issues/22024
- https://github.com/rocq-prover/rocq/pull/22027
- https://github.com/rocq-prover/rocq
- https://github.com/endrazine/rocq-cve-poc-22024
