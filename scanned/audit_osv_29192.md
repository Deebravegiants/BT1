# [H] net: bridge: mst: fix suspicious rcu usage in br_mst_set_state

## Summary
Severity: High
Advisory: CVE-2024-40920
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40920
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.93 <6.1.95, >=6.6.33 <6.6.35, >=6.9.3 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bridge: mst: fix suspicious rcu usage in br_mst_set_state

I converted br_mst_set_state to RCU to avoid a vlan use-after-free
but forgot to change the vlan group dereference helper. Switch to vlan
group RCU deref helper to fix the suspicious rcu usage warning.

## References
- https://git.kernel.org/stable/c/406bfc04b01ee47e4c626f77ecc7d9f85135b166
- https://git.kernel.org/stable/c/546ceb1dfdac866648ec959cbc71d9525bd73462
- https://git.kernel.org/stable/c/7caefa2771722e65496d85b62e1dc4442b7d1345
- https://git.kernel.org/stable/c/caaa2129784a04dcade0ea92c12e6ff90bbd23d8
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40920.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40920
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
