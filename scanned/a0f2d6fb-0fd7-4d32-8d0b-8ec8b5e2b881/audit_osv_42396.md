# [H] CVE-2026-67846

## Summary
Severity: High
Advisory: CVE-2026-67846
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-67846
Type: osv

## Details
Berkeley Out-of-Order Machine (BOOM) commit 5223e44cfeb26f41380057a2eb4d651197475f69 contains a potential incorrect privilege assignment issue in the v3 and v4 NBDTLB implementations. The raw mstatus.SUM value participates in the read and write permission logic without an explicit local satp.MODE validity check at the use site

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67846.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67846
- https://github.com/riscv-boom/riscv-boom/commit/5223e44cfeb26f41380057a2eb4d651197475f69
- https://github.com/duan528/CVE-2026-67846-BOOM-NBDTLB
- https://github.com/riscv-boom/riscv-boom
