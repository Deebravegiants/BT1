# [C] netfilter: flowtable: IPIP tunnel hardware offload is not yet support

## Summary
Severity: Critical
Advisory: CVE-2026-64410
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64410
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: flowtable: IPIP tunnel hardware offload is not yet support

No driver supports for IPIP tunnels yet, give up early on setting up the
hardware offload for this scenario.

This patch adds a stub that can be enhanced to add more configuration
that are currently not supported. As of now, the offload work is
enqueued to the worker, then ignored if the hardware offload
configuration is not supported.

Check the NF_FLOW_HW flag to know if this entry was already tried once
to be offloaded so this is not retried on refresh when unsupported. Move
NF_FLOW_HW flag check to nf_flow_offload_add(). If this NF_FLOW_HW flag
is unset the _del and _stats variants are never called.

This can be updated later on to skip hardware offload work to be queued
in case hardware offload does not support it.

## References
- https://git.kernel.org/stable/c/6c5dcab95f4cd42a1648739ec9300fbb4b1a021f
- https://git.kernel.org/stable/c/9efe838c13133acb70c78d04c49e8362fe533566
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64410.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64410
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
