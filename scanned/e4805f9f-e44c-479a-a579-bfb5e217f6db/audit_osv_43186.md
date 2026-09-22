# [M] Rocq Prover through 9.2.0 Universe Checking State Desynchronised After Module Close

## Summary
Severity: Medium
Advisory: CVE-2026-72714
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-72714
Type: osv

## Details
Rocq Prover does not restore the universe graph's copy of the universe checking flag when a module that locally disabled the check is closed. Local Unset Universe Checking inside a module is expected to last only until the module ends, and the global flag is restored, but the universe graph keeps its own copy which is left disabled. The two views then disagree: Test Universe Checking reports the check as enabled while the kernel continues to accept universe-inconsistent terms. With the constraint between two universes no longer enforced, Hurkens' paradox applies and yields a proof of False, from which any proposition follows. The proof uses no axioms, plugins or unsafe features once the module has closed, and Print Assumptions reports it as closed under the global context, so neither the assumption audit nor the flag query reflects the actual kernel state. No fix is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72714.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72714
- https://www.vulncheck.com/advisories/rocq-prover-through-universe-checking-state-desynchronised-after-module-close
- https://github.com/rocq-prover/rocq/issues/22287
- https://github.com/rocq-prover/rocq
- https://github.com/endrazine/rocq-cve-poc-22287
