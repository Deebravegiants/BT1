# [C] netfilter: flowtable: Validate iph->ihl in nf_flow_ip4_tunnel_proto()

## Summary
Severity: Critical
Advisory: CVE-2026-72417
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72417
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: flowtable: Validate iph->ihl in nf_flow_ip4_tunnel_proto()

Add sanity check for iph->ihl field in nf_flow_ip4_tunnel_proto() before
using it to compute the header size, avoiding out-of-bounds access with
malformed IP headers.
While at it, use iph->protocol instead of the hardcoded IPPROTO_IPIP
constant when setting ctx->tun.proto and reference ctx->tun.hdr_size
when updating ctx->offset.

## References
- https://git.kernel.org/stable/c/025a41e76b51fbc7b8eaa5bacbaa9621d00e6aa7
- https://git.kernel.org/stable/c/84460b644329e25809b4a6d9279d6359d7fd8ebc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72417.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72417
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
