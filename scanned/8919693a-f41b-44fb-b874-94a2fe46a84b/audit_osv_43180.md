# [M] Rocq Prover 8.20 before 9.2.0 Guard Checker Accepts Non-Terminating Fixpoint via Unchecked Cross-Calls

## Summary
Severity: Medium
Advisory: CVE-2026-72703
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-72703
Type: osv

## Details
The guard checker in Rocq Prover treats a parameter of a nested mutual fixpoint as uniform without examining calls between the different bodies of that fixpoint. find_uniform_parameters in kernel/inductive.ml inspects only self-recursive calls, so when no body calls itself the function concludes that every parameter is uniform. A parameter that grows through a cross-call from one body to another therefore keeps the subterm specification it inherited from the enclosing fixpoint, and a recursive call guarded by that specification is accepted although the argument is not structurally smaller. A non-terminating definition is admitted as structurally decreasing, which yields a term whose value equals its own successor and so a proof of False, from which any proposition follows. The proof requires no axioms, plugins or unsafe flags and Print Assumptions reports it as closed under the global context. Introduced in Coq 8.20 and fixed in Rocq 9.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72703.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72703
- https://www.vulncheck.com/advisories/rocq-prover-before-guard-checker-accepts-non-terminating-fixpoint-via-unchecked-cross-calls
- https://github.com/rocq-prover/rocq/issues/21682
- https://github.com/rocq-prover/rocq/pull/21684
- https://github.com/rocq-prover/rocq
- https://github.com/endrazine/rocq-cve-poc-21682
