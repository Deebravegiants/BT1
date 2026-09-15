# [H] netfilter: nf_tables: reject duplicate device on updates

## Summary
Severity: High
Advisory: CVE-2025-38678
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-03
Source: https://osv.dev/vulnerability/CVE-2025-38678
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.59, >=6.13.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: reject duplicate device on updates

A chain/flowtable update with duplicated devices in the same batch is
possible. Unfortunately, netdev event path only removes the first
device that is found, leaving unregistered the hook of the duplicated
device.

Check if a duplicated device exists in the transaction batch, bail out
with EEXIST in such case.

WARNING is hit when unregistering the hook:

 [49042.221275] WARNING: CPU: 4 PID: 8425 at net/netfilter/core.c:340 nf_hook_entry_head+0xaa/0x150
 [49042.221375] CPU: 4 UID: 0 PID: 8425 Comm: nft Tainted: G S                  6.16.0+ #170 PREEMPT(full)
 [...]
 [49042.221382] RIP: 0010:nf_hook_entry_head+0xaa/0x150

## References
- https://git.kernel.org/stable/c/0521e694d5b80899fba8695881a6349f9bc538cb
- https://git.kernel.org/stable/c/3f358a66a04513311668ea4b40f5064e253d8386
- https://git.kernel.org/stable/c/4681960bc0f4f8bcc782cbf2fd205f48ad314dfd
- https://git.kernel.org/stable/c/4ce2a0c3b8497a66cfc25fc7ca3d087258a785d2
- https://git.kernel.org/stable/c/cf23d531a9d496863aa4c5a0e2f71f0a23f3df3c
- https://git.kernel.org/stable/c/cf5fb87fcdaaaafec55dcc0dc5a9e15ead343973
- https://git.kernel.org/stable/c/d7615bde541f16517d6790412da6ec46fa8a4c1f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38678.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38678
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
