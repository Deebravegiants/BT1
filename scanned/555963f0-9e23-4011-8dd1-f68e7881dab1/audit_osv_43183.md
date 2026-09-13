# [M] Lean 4 before 4.32.2 Kernel Accepts Opaque Declaration With an Unbound Free Variable

## Summary
Severity: Medium
Advisory: CVE-2026-72711
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-72711
Type: osv

## Details
The Lean 4 kernel does not check that the body of an opaque declaration is closed. environment::add_opaque omits the check_no_metavar_no_fvar call that the definition and theorem paths perform, so a value containing a free variable that is absent from the local context is not rejected outright. A metaprogram can first cause the kernel to create a temporary local of type False and record its type in the type checker's inference cache, then restore the local context while that cache entry persists on the same type checker instance, and finally submit an opaque declaration whose value is the now-unbound variable. The cache lookup answers before the branch that would test membership of the local context, so the kernel infers the cached type and admits an opaque constant of type False, from which any proposition follows. The declaration is accepted through the ordinary checked path at maximum kernel checking, without sorry, unsafeCast, debug.skipKernelTC, addDeclWithoutChecking, foreign code or a modified .olean file, and the result carries no axioms. Fixed in 4.32.2 by adding the missing closure check.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72711.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72711
- https://www.vulncheck.com/advisories/lean-4-before-kernel-accepts-opaque-declaration-with-an-unbound-free-variable
- https://github.com/leanprover/lean4/issues/14484
- https://github.com/leanprover/lean4/pull/14498
- https://github.com/leanprover/lean4
- https://github.com/endrazine/lean-cve-poc-14484
