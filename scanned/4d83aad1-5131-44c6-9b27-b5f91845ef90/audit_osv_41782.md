# [H] bpf: Drop task_to_inode and inet_conn_established from lsm sleepable hooks

## Summary
Severity: High
Advisory: CVE-2026-63865
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63865
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Drop task_to_inode and inet_conn_established from lsm sleepable hooks

bpf_lsm_task_to_inode() is called under rcu_read_lock() and
bpf_lsm_inet_conn_established() is called from softirq context, so
neither hook can be used by sleepable LSM programs.

## References
- https://git.kernel.org/stable/c/0d918263c9bfc86078edb2e2f7302a0c6ce42b7c
- https://git.kernel.org/stable/c/26b380a3ca0b605fd8860995ed6a208f276dd316
- https://git.kernel.org/stable/c/281f2a214565a5cbf8b7355a65738d80bd19b8c5
- https://git.kernel.org/stable/c/452a927cddcd67478d030e646f41cb904a93156f
- https://git.kernel.org/stable/c/989f1b93907de1753a814996222da375f07e579b
- https://git.kernel.org/stable/c/beaf0e96b1da74549a6cabd040f9667d83b2e97e
- https://git.kernel.org/stable/c/f0fc2a9828171205244a28013f02889f50b71c9f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63865.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63865
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
