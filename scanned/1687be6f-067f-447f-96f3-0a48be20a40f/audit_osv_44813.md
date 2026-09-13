# [M] mrubyc through 4.0.0 NULL Pointer Dereference via OP_ENTER

## Summary
Severity: Medium
Advisory: CVE-2026-86547
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86547
Type: osv

## Details
mrubyc through 4.0.0 contains a null pointer dereference vulnerability in the op_enter() handler in src/vm.c when processing untrusted bytecode. Attackers can craft malicious .mrb bytecode files with OP_ENTER instructions at the top level to crash the embedding application and cause denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86547.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86547
- https://www.vulncheck.com/advisories/mrubyc-through-4.0.0-null-pointer-dereference-via-op-enter
- https://github.com/mrubyc/mrubyc
- https://github.com/mrubyc/mrubyc/blob/4261cf5e5ae5579e3110dab98a04b91c7d919429/src/vm.c#L1534
- https://github.com/mrubyc/mrubyc/blob/release4.0.0/src/vm.c#L1537
