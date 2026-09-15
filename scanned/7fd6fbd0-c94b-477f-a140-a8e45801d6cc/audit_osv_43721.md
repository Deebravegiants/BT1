# [H] netfilter: bridge: release template ct on non-IP path

## Summary
Severity: High
Advisory: CVE-2026-74625
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74625
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: bridge: release template ct on non-IP path

A bridge nftables ct zone set rule can attach a conntrack template to
an skb before nf_ct_bridge_pre() sees it. For non-IPv4 and non-IPv6
EtherTypes, nf_ct_bridge_pre() currently overwrites skb->_nfct with
IP_CT_UNTRACKED without releasing the existing template reference.

That makes the per-cpu template, and any temporary templates allocated
for concurrent use, unreachable and leaks memory until the host runs out
of slab.

Reset the skb conntrack state before marking the frame untracked so the
existing template reference is dropped on the non-IP path.

## References
- https://git.kernel.org/stable/c/46d559f00b1ab1d114f92d2f16c5ef0093b3b9dd
- https://git.kernel.org/stable/c/6ea88401e10e04e0b3bb7a7adea54932fb60b93b
- https://git.kernel.org/stable/c/7cff440d702616022769f2643168d7f9820547a0
- https://git.kernel.org/stable/c/bd7b16494dacf87e9336a1dcfdada83b9e40edd6
- https://git.kernel.org/stable/c/c58d34fe8b7e47bb0b350a7625023b1261342be5
- https://git.kernel.org/stable/c/d45cc8020d7c0a9f01dee42ff5c40bc14c9af72f
- https://git.kernel.org/stable/c/daa6e070f8e1e7a4dddec8b64ca37663f8cda917
- https://git.kernel.org/stable/c/fc90df37540627d092af770215fb4b7befe9409b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74625.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74625
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
