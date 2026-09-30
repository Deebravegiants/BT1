# [H] sched_ext: Validate prev_cpu in scx_bpf_select_cpu_dfl()

## Summary
Severity: High
Advisory: CVE-2025-21965
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21965
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched_ext: Validate prev_cpu in scx_bpf_select_cpu_dfl()

If a BPF scheduler provides an invalid CPU (outside the nr_cpu_ids
range) as prev_cpu to scx_bpf_select_cpu_dfl() it can cause a kernel
crash.

To prevent this, validate prev_cpu in scx_bpf_select_cpu_dfl() and
trigger an scx error if an invalid CPU is specified.

## References
- https://git.kernel.org/stable/c/515680e76c536dd4aa8e2b5d674b0d441baddf5b
- https://git.kernel.org/stable/c/752b56bb76e2471197d25d6948d85753043b10da
- https://git.kernel.org/stable/c/9360dfe4cbd62ff1eb8217b815964931523b75b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21965.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21965
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
