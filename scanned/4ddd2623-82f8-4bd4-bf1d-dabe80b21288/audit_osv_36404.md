# [H] netfilter: bpf: defer hook memory release until rcu readers are done

## Summary
Severity: High
Advisory: CVE-2026-23412
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-23412
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: bpf: defer hook memory release until rcu readers are done

Yiming Qian reports UaF when concurrent process is dumping hooks via
nfnetlink_hooks:

BUG: KASAN: slab-use-after-free in nfnl_hook_dump_one.isra.0+0xe71/0x10f0
Read of size 8 at addr ffff888003edbf88 by task poc/79
Call Trace:
 <TASK>
 nfnl_hook_dump_one.isra.0+0xe71/0x10f0
 netlink_dump+0x554/0x12b0
 nfnl_hook_get+0x176/0x230
 [..]

Defer release until after concurrent readers have completed.

## References
- https://git.kernel.org/stable/c/24f90fa3994b992d1a09003a3db2599330a5232a
- https://git.kernel.org/stable/c/54244d54a971c26a0cd0a9073460ff71f3c51b32
- https://git.kernel.org/stable/c/c25e0dec366ae99b7264324ce3c7cbaea34691f9
- https://git.kernel.org/stable/c/cb2bf5efdb02a2a59faf603604a1066e8266f349
- https://git.kernel.org/stable/c/d016c216bc75c45128160593a77b864a04dbe7c0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23412.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23412
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
