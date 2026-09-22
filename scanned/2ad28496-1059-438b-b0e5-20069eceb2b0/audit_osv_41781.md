# [H] bpf: Propagate error from visit_tailcall_insn

## Summary
Severity: High
Advisory: CVE-2026-63864
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63864
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Propagate error from visit_tailcall_insn

Commit e40f5a6bf88a ("bpf: correct stack liveness for tail calls") added
visit_tailcall_insn() but did not check its return value.

## References
- https://git.kernel.org/stable/c/6bd96e40f31dde8f8cd79772b4df0f171cf8a915
- https://git.kernel.org/stable/c/945816e63c8677cf4bfde963a0774432ce8afc85
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63864.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63864
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
