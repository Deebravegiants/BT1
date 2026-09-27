# [H] idpf: fix kernel panic on unknown packet types

## Summary
Severity: High
Advisory: CVE-2024-35889
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35889
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

idpf: fix kernel panic on unknown packet types

In the very rare case where a packet type is unknown to the driver,
idpf_rx_process_skb_fields would return early without calling
eth_type_trans to set the skb protocol / the network layer handler.
This is especially problematic if tcpdump is running when such a
packet is received, i.e. it would cause a kernel panic.

Instead, call eth_type_trans for every single packet, even when
the packet type is unknown.

## References
- https://git.kernel.org/stable/c/b4d28f7fa4dd531cf503a4fe1ca7008960cc5832
- https://git.kernel.org/stable/c/dd19e827d63ac60debf117676d1126bff884bdb8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35889.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35889
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
