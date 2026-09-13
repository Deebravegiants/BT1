# [C] PREVAIL: Non-singleton typeset in add() skips offset update, allowing OOB access to pass eBPF verification

## Summary
Severity: Critical
Advisory: CVE-2026-53670
Aliases: GHSA-2qc8-qh94-66rc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-53670
Type: osv

## Details
PREVAIL is a Polynomial-Runtime EBPF Verifier using an Abstract Interpretation Layer. Prior to version 0.2.4, in the Prevail eBPF verifier, EbpfTransformer::add() silently skips offset-variable updates when the destination register carries a non-singleton typeset (two or more simultaneously possible pointer types). Subsequent bounds checks use the stale offset and accept out-of-bounds memory accesses, so a crafted BPF program passes verification even though it would corrupt memory at runtime. This issue has been patched in version 0.2.4.

## References
- https://github.com/vbpf/prevail/releases/tag/v0.2.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53670.json
- https://github.com/vbpf/prevail/security/advisories/GHSA-2qc8-qh94-66rc
- https://nvd.nist.gov/vuln/detail/CVE-2026-53670
- https://github.com/vbpf/prevail/commit/2b209bc4e3d612ff9aca87125e67c0ff84477e61
