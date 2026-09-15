# [H] bpf: Fix metadata_dst leak __bpf_redirect_neigh_v{4,6}

## Summary
Severity: High
Advisory: CVE-2025-40183
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40183
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.157, >=6.2.0 <6.6.113, >=6.7.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix metadata_dst leak __bpf_redirect_neigh_v{4,6}

Cilium has a BPF egress gateway feature which forces outgoing K8s Pod
traffic to pass through dedicated egress gateways which then SNAT the
traffic in order to interact with stable IPs outside the cluster.

The traffic is directed to the gateway via vxlan tunnel in collect md
mode. A recent BPF change utilized the bpf_redirect_neigh() helper to
forward packets after the arrival and decap on vxlan, which turned out
over time that the kmalloc-256 slab usage in kernel was ever-increasing.

The issue was that vxlan allocates the metadata_dst object and attaches
it through a fake dst entry to the skb. The latter was never released
though given bpf_redirect_neigh() was merely setting the new dst entry
via skb_dst_set() without dropping an existing one first.

## References
- https://git.kernel.org/stable/c/057764172fcc6ee2ccb6c41351a55a9f054dc8fd
- https://git.kernel.org/stable/c/23f3770e1a53e6c7a553135011f547209e141e72
- https://git.kernel.org/stable/c/2e67c2037382abb56497bb9d7b7e10be04eb5598
- https://git.kernel.org/stable/c/3fba965a9aac0fa3cbd8138436a37af9ab466d79
- https://git.kernel.org/stable/c/7404ce888a45eb7da0508b7cbbe6f2e95302eeb8
- https://git.kernel.org/stable/c/b6bfe44b6dbb14a31d86c475cdc9c7689534fb09
- https://git.kernel.org/stable/c/f36a305d30f557306d87c787ddffe094ac5dac89
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40183.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40183
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
