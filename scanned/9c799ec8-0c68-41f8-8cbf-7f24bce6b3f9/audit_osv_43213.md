# [M] Lean 4 Kernel Type Checking Bypass via Mismatched Structure Projections

## Summary
Severity: Medium
Advisory: CVE-2026-72844
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-72844
Type: osv

## Details
The Lean 4 kernel does not verify that the structure named in a projection expression matches the type of the value being projected, and environment::add_inductive in src/kernel/inductive.cpp did not type check the nested inductive applications that are replaced by auxiliary types, so their parametric arguments escaped checking. A metaprogram running in the Lean process can register an ill-typed nested inductive whose constructor applies a .proj C 0 projection to a value of the unrelated type W, and the kernel admits the declaration through the ordinary checked addDecl path at maximum kernel checking, without sorry, unsafeCast, debug.skipKernelTC, addDeclWithoutChecking, FFI, or a modified .olean file. The result is a type confusion yielding a proof of False that carries no axioms, from which any proposition can be derived. The published proof of concept additionally pads two expressions until their hashes and approximate depths collide, which defeats kernel caching; that is the technique used to reach the flaw, not its cause. Exploitation requires running a metaprogram in-process, for example by building a project or importing a malicious Lake dependency.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72844.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72844
- https://www.openwall.com/lists/oss-security/2026/08/02/1
- https://www.vulncheck.com/advisories/lean-4-kernel-type-checking-bypass-via-mismatched-structure-projections
- https://github.com/leanprover/lean4/issues/14576
- https://github.com/leanprover/lean4/pull/14577
- https://github.com/leanprover/lean4/commit/a39eab69e1eee9ad38f4efe507907b1026a77808
- https://github.com/leanprover/lean4
- https://github.com/endrazine/lean-cve-poc
- https://github.com/xrchz/CollatzLean
