# [H] mptcp: fix race in mptcp_pm_nl_flush_addrs_doit()

## Summary
Severity: High
Advisory: CVE-2026-23169
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23169
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.201, >=5.16.0 <6.1.164, >=6.2.0 <6.6.125, >=6.7.0 <6.12.72, >=6.13.0 <6.18.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix race in mptcp_pm_nl_flush_addrs_doit()

syzbot and Eulgyu Kim reported crashes in mptcp_pm_nl_get_local_id()
and/or mptcp_pm_nl_is_backup()

Root cause is list_splice_init() in mptcp_pm_nl_flush_addrs_doit()
which is not RCU ready.

list_splice_init_rcu() can not be called here while holding pernet->lock
spinlock.

Many thanks to Eulgyu Kim for providing a repro and testing our patches.

## References
- https://git.kernel.org/stable/c/1f1b9523527df02685dde603f20ff6e603d8e4a1
- https://git.kernel.org/stable/c/338d40bab283da2639780ee3e458fb61f1567d8c
- https://git.kernel.org/stable/c/455e882192c9833f176f3fbbbb2f036b6c5bf555
- https://git.kernel.org/stable/c/51223bdd0f60b06cfc7f25885c4d4be917adba94
- https://git.kernel.org/stable/c/7896dbe990d56d5bb8097863b2645355633665eb
- https://git.kernel.org/stable/c/e2a9eeb69f7d4ca4cf4c70463af77664fdb6ab1d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23169.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23169
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
