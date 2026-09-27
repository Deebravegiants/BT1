# [H] PREVAIL: ALU32 pointer arithmetic accepted without is64 gate — verifier emits false PASS for pointer-corrupting programs

## Summary
Severity: High
Advisory: CVE-2026-53706
Aliases: GHSA-65fp-5qmq-gg2m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-53706
Type: osv

## Details
PREVAIL is a Polynomial-Runtime EBPF Verifier using an Abstract Interpretation Layer. Prior to version 0.2.4, the prevail eBPF verifier accepts ALU32 ADD and SUB instructions that operate on pointer-typed registers without checking the is64 flag. Because ALU32 arithmetic zero-extends the 32-bit result, the upper half of any pointer is silently destroyed at runtime, yet prevail marks the program as verified safe. Any caller that can submit an eBPF program for verification — including unprivileged users on kernels that permit BPF program loading — can produce a program that passes verification but faults or misbehaves at runtime. This issue has been patched in version 0.2.4.

## References
- https://github.com/vbpf/prevail/releases/tag/v0.2.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53706.json
- https://github.com/vbpf/prevail/security/advisories/GHSA-65fp-5qmq-gg2m
- https://nvd.nist.gov/vuln/detail/CVE-2026-53706
- https://github.com/vbpf/prevail/commit/d3fab8c23a93d9a615bc741b254ab26391559e0f
