# [C] ipvs: clear IPv4 options after rebasing tunnel ICMP errors

## Summary
Severity: Critical
Advisory: CVE-2026-74669
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74669
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: clear IPv4 options after rebasing tunnel ICMP errors

ip_vs_in_icmp() rebases an skb from the outer ICMP packet to the
quoted original request before passing it to icmp_send(). However,
IPCB(skb)->opt still describes the outer IPv4 header.

A timestamp option in the outer header can therefore leave an offset
that points into the quoted transport header after the rebase.
__ip_options_echo() treats a byte at that stale location as the option
length and copies it into the fixed-size option storage on the
__icmp_send() stack, causing a stack out-of-bounds write.

Clear the stale option metadata after resetting the network header.
Keep the remaining control block fields, including the ingress
interface used by the ICMP response path.

## References
- https://git.kernel.org/stable/c/37c61b3745129cbd682c557b51345828120972e5
- https://git.kernel.org/stable/c/384b4dae14277d369221d187e9b3af56c79d2e50
- https://git.kernel.org/stable/c/6f46fc460e9316062bdcdf89199eb5d7a33da33b
- https://git.kernel.org/stable/c/75eec935444db4af2123e0491936f6e273d7ea00
- https://git.kernel.org/stable/c/79ffa99202c944467e28b13b513bf2998732edff
- https://git.kernel.org/stable/c/c9413b50204738fbc429bb86bf01353c393a6c28
- https://git.kernel.org/stable/c/e0ba936287dfe9783426aac27e5fd76fe35b38c9
- https://git.kernel.org/stable/c/ed246dd85ebf27c1f6b7897834d40786c0ca3006
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74669.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74669
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
