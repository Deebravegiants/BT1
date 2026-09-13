# [M] Rocq Prover before 9.2.0 Guard Checker Accepts Fixpoint Passed as a Higher-Order Argument

## Summary
Severity: Medium
Advisory: CVE-2026-72705
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-72705
Type: osv

## Details
The guard checker in Rocq Prover does not follow recursive calls made through a fixpoint's own arguments. A fixpoint may pass itself as a higher-order argument to a second fixpoint, which then applies it to a value that is not a subterm of the structural argument. Passing the recursive function to a plain definition is rejected because the checker unfolds the definition and observes the call, but passing it to a fixpoint is accepted because higher-order recursive calls through fixpoint arguments are not tracked. This admits a type that is definitionally equal to its own negation, so self-application produces False in purely definitional code, without tactics, axioms, plugins or unsafe flags, and Print Assumptions reports the result as closed under the global context. Fixed in Rocq 9.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72705.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72705
- https://www.vulncheck.com/advisories/rocq-prover-before-guard-checker-accepts-fixpoint-passed-as-a-higher-order-argument
- https://github.com/rocq-prover/rocq/issues/21683
- https://github.com/rocq-prover/rocq/pull/21684
- https://github.com/rocq-prover/rocq
- https://github.com/endrazine/rocq-cve-poc-21683
