# [H] tcp: add accessors to read/set tp->snd_cwnd

## Summary
Severity: High
Advisory: CVE-2022-49325
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49325
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.17 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: add accessors to read/set tp->snd_cwnd

We had various bugs over the years with code
breaking the assumption that tp->snd_cwnd is greater
than zero.

Lately, syzbot reported the WARN_ON_ONCE(!tp->prior_cwnd) added
in commit 8b8a321ff72c ("tcp: fix zero cwnd in tcp_cwnd_reduction")
can trigger, and without a repro we would have to spend
considerable time finding the bug.

Instead of complaining too late, we want to catch where
and when tp->snd_cwnd is set to an illegal value.

## References
- https://git.kernel.org/stable/c/3308676ec525901bf1656014003c443a60730a04
- https://git.kernel.org/stable/c/40570375356c874b1578e05c1dcc3ff7c1322dbe
- https://git.kernel.org/stable/c/41e191fe72282e193a7744e2fc1786b23156c9e4
- https://git.kernel.org/stable/c/5aba0ad44fb4a7fb78c5076c313456de199a3c29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49325.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49325
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
