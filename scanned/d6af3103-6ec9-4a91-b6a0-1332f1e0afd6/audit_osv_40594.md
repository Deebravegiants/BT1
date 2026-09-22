# [H] PREVAIL: Context-write no-op in do_mem_store allows unsafe eBPF programs to pass verification

## Summary
Severity: High
Advisory: CVE-2026-53671
Aliases: GHSA-65rv-h458-cq99
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-53671
Type: osv

## Details
PREVAIL is a Polynomial-Runtime EBPF Verifier using an Abstract Interpretation Layer. Prior to version 0.2.4, the abstract transformer in prevail treats writes through a T_CTX-typed base register as a silent no-op: do_mem_store in src/crab/ebpf_transformer.cpp only models T_STACK stores, and the checker's T_CTX bounds arm never tests AccessType::write. An attacker can craft an eBPF program that overwrites a context field (e.g., ctx->data), reload that field typed as T_PACKET, and dereference an attacker-controlled address — and prevail will report the program as safe. This issue has been patched in version 0.2.4.

## References
- https://github.com/vbpf/prevail/releases/tag/v0.2.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53671.json
- https://github.com/vbpf/prevail/security/advisories/GHSA-65rv-h458-cq99
- https://nvd.nist.gov/vuln/detail/CVE-2026-53671
- https://github.com/vbpf/prevail/commit/de65234f67d2608b54d12571edb585ead224363c
