# [H] team: fix null-ptr-deref when team device type is changed

## Summary
Severity: High
Advisory: CVE-2023-52574
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52574
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.14.327, >=4.15.0 <4.19.296, >=4.20.0 <5.4.258, >=5.5.0 <5.10.198, >=5.11.0 <5.15.134, >=5.16.0 <6.1.56, >=6.2.0 <6.5.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

team: fix null-ptr-deref when team device type is changed

Get a null-ptr-deref bug as follows with reproducer [1].

BUG: kernel NULL pointer dereference, address: 0000000000000228
...
RIP: 0010:vlan_dev_hard_header+0x35/0x140 [8021q]
...
Call Trace:
 <TASK>
 ? __die+0x24/0x70
 ? page_fault_oops+0x82/0x150
 ? exc_page_fault+0x69/0x150
 ? asm_exc_page_fault+0x26/0x30
 ? vlan_dev_hard_header+0x35/0x140 [8021q]
 ? vlan_dev_hard_header+0x8e/0x140 [8021q]
 neigh_connected_output+0xb2/0x100
 ip6_finish_output2+0x1cb/0x520
 ? nf_hook_slow+0x43/0xc0
 ? ip6_mtu+0x46/0x80
 ip6_finish_output+0x2a/0xb0
 mld_sendpack+0x18f/0x250
 mld_ifc_work+0x39/0x160
 process_one_work+0x1e6/0x3f0
 worker_thread+0x4d/0x2f0
 ? __pfx_worker_thread+0x10/0x10
 kthread+0xe5/0x120
 ? __pfx_kthread+0x10/0x10
 ret_from_fork+0x34/0x50
 ? __pfx_kthread+0x10/0x10
 ret_from_fork_asm+0x1b/0x30

[1]
$ teamd -t team0 -d -c '{"runner": {"name": "loadbalance"}}'
$ ip link add name t-dummy type dummy
$ ip link add link t-dummy name t-dummy.100 type vlan id 100
$ ip link add name t-nlmon type nlmon
$ ip link set t-nlmon master team0
$ ip link set t-nlmon nomaster
$ ip link set t-dummy up
$ ip link set team0 up
$ ip link set t-dummy.100 down
$ ip link set t-dummy.100 master team0

When enslave a vlan device to team device and team device type is changed
from non-ether to ether, header_ops of team device is changed to
vlan_header_ops. That is incorrect and will trigger null-ptr-deref
for vlan->real_dev in vlan_dev_hard_header() because team device is not
a vlan device.

Cache eth_header_ops in team_setup(), then assign cached header_ops to
header_ops of team net device when its type is changed from non-ether
to ether to fix the bug.

## References
- https://git.kernel.org/stable/c/1779eb51b9cc628cee551f252701a85a2a50a457
- https://git.kernel.org/stable/c/2f0acb0736ecc3eb85dc80ad2790d634dcb10b58
- https://git.kernel.org/stable/c/492032760127251e5540a5716a70996bacf2a3fd
- https://git.kernel.org/stable/c/a7fb47b9711101d2405b0eb1276fb1f9b9b270c7
- https://git.kernel.org/stable/c/b44dd92e2afd89eb6e9d27616858e72a67bdc1a7
- https://git.kernel.org/stable/c/c5f6478686bb45f453031594ae19b6c9723a780d
- https://git.kernel.org/stable/c/cac50d9f5d876be32cb9aa21c74018468900284d
- https://git.kernel.org/stable/c/cd05eec2ee0cc396813a32ef675634e403748255
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52574.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52574
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
