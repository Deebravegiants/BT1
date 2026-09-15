# [H] netfilter: bpf: must hold reference on net namespace

## Summary
Severity: High
Advisory: CVE-2024-50130
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50130
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: bpf: must hold reference on net namespace

BUG: KASAN: slab-use-after-free in __nf_unregister_net_hook+0x640/0x6b0
Read of size 8 at addr ffff8880106fe400 by task repro/72=
bpf_nf_link_release+0xda/0x1e0
bpf_link_free+0x139/0x2d0
bpf_link_release+0x68/0x80
__fput+0x414/0xb60

Eric says:
 It seems that bpf was able to defer the __nf_unregister_net_hook()
 after exit()/close() time.
 Perhaps a netns reference is missing, because the netns has been
 dismantled/freed already.
 bpf_nf_link_attach() does :
 link->net = net;
 But I do not see a reference being taken on net.

Add such a reference and release it after hook unreg.
Note that I was unable to get syzbot reproducer to work, so I
do not know if this resolves this splat.

## References
- https://git.kernel.org/stable/c/1230fe7ad3974f7bf6c78901473e039b34d4fb1f
- https://git.kernel.org/stable/c/d0d7939543a1b3bb93af9a18d258a774daf8f162
- https://git.kernel.org/stable/c/f41bd93b3e0508edc7ba820357f949071dcc0acc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50130.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50130
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
