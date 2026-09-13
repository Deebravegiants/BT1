# [H] mptcp: Use __sk_dst_get() and dst_dev_rcu() in mptcp_active_enable().

## Summary
Severity: High
Advisory: CVE-2025-40133
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40133
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.55, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: Use __sk_dst_get() and dst_dev_rcu() in mptcp_active_enable().

mptcp_active_enable() is called from subflow_finish_connect(),
which is icsk->icsk_af_ops->sk_rx_dst_set() and it's not always
under RCU.

Using sk_dst_get(sk)->dev could trigger UAF.

Let's use __sk_dst_get() and dst_dev_rcu().

## References
- https://git.kernel.org/stable/c/893c49a78d9f85e4b8081b908fb7c407d018106a
- https://git.kernel.org/stable/c/ad16235c9d3ef7ec17c109ff39b7504f49d17072
- https://git.kernel.org/stable/c/cc976ec9e38bb79409de3261ba1dbb6868e2a53e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40133.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40133
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
