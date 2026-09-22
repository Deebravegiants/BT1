# [H] firewire: net: fix use after free in fwnet_finish_incoming_packet()

## Summary
Severity: High
Advisory: CVE-2023-53432
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53432
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <5.15.128, >=5.16.0 <6.1.47, >=6.2.0 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

firewire: net: fix use after free in fwnet_finish_incoming_packet()

The netif_rx() function frees the skb so we can't dereference it to
save the skb->len.

## References
- https://git.kernel.org/stable/c/2ea70379e4f4efa95c9daa7f3f9bdd4d40aec927
- https://git.kernel.org/stable/c/3ff256751a2853e1ffaa36958ff933ccc98c6cb5
- https://git.kernel.org/stable/c/9040adc38cf6bfbb77034d558ac2c52f70d840ac
- https://git.kernel.org/stable/c/9860921ab4521252dc39bb21b9c936bd09a00982
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53432.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53432
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
