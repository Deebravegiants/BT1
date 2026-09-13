# [H] netfilter: conntrack: Avoid nf_ct_helper_hash uses after free

## Summary
Severity: High
Advisory: CVE-2023-53619
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53619
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <4.14.322, >=4.15.0 <4.19.291, >=4.20.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: conntrack: Avoid nf_ct_helper_hash uses after free

If nf_conntrack_init_start() fails (for example due to a
register_nf_conntrack_bpf() failure), the nf_conntrack_helper_fini()
clean-up path frees the nf_ct_helper_hash map.

When built with NF_CONNTRACK=y, further netfilter modules (e.g:
netfilter_conntrack_ftp) can still be loaded and call
nf_conntrack_helpers_register(), independently of whether nf_conntrack
initialized correctly. This accesses the nf_ct_helper_hash dangling
pointer and causes a uaf, possibly leading to random memory corruption.

This patch guards nf_conntrack_helper_register() from accessing a freed
or uninitialized nf_ct_helper_hash pointer and fixes possible
uses-after-free when loading a conntrack module.

## References
- https://git.kernel.org/stable/c/00716f25f9697d02a0d9bd622575c7c7321ba3d0
- https://git.kernel.org/stable/c/05561f822f27b9fa88fa5504ddec34bf38833034
- https://git.kernel.org/stable/c/4ee69c91cb8f9ca144bc0861969e5a1a3c6152a7
- https://git.kernel.org/stable/c/61c7a5256543ae7d24cd9d21853d514c8632e1e9
- https://git.kernel.org/stable/c/6eef7a2b933885a17679eb8ed0796ddf0ee5309b
- https://git.kernel.org/stable/c/6f03ce2f1abcb9f9d0511e3659ca6eb60e39f566
- https://git.kernel.org/stable/c/8289d422f5e484efe4a565fe18e862ecd621c175
- https://git.kernel.org/stable/c/fce5cc7cbd4b92f979bf02c9ec5fb69aaeba92d7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53619.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53619
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
