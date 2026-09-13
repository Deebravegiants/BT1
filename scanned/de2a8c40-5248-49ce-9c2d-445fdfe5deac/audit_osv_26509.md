# [M] samples/bpf: Fix fout leak in hbm's run_bpf_prog

## Summary
Severity: Medium
Advisory: CVE-2023-53290
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53290
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

samples/bpf: Fix fout leak in hbm's run_bpf_prog

Fix fout being fopen'ed but then not subsequently fclose'd. In the affected
branch, fout is otherwise going out of scope.

## References
- https://git.kernel.org/stable/c/23acb14af1914010dd0aae1bbb7fab28bf518b8e
- https://git.kernel.org/stable/c/7560ed6592ff4077528c239c71e91b19de985b97
- https://git.kernel.org/stable/c/a7ec2f424f6edad34651137783a0a59eca9aa37e
- https://git.kernel.org/stable/c/e3e6e252d74f20f6fc610c7fef3ae7dda0109a6f
- https://git.kernel.org/stable/c/edf37bc8b03d3f948e679b2fd2d14464495f5d1b
- https://git.kernel.org/stable/c/f2065b8b0a215bc6aa061287a2e3d9eab2446422
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53290.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53290
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
