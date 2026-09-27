# [C] batman-adv: dat: acquire ARP hw source only after skb realloc

## Summary
Severity: Critical
Advisory: CVE-2026-80600
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80600
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: dat: acquire ARP hw source only after skb realloc

The pskb_may_pull() called by batadv_get_vid() could reallocate the buffer
behind the skb. Variables which were pointing to the old buffer need to be
reassigned to avoid an use-after-free.

## References
- https://git.kernel.org/stable/c/01678c53a7717a748aee388b6839e7b9761d641c
- https://git.kernel.org/stable/c/059a70e1d12d6d99310e0599d37b0323557569a8
- https://git.kernel.org/stable/c/3404be97b940a9b1ae1aea5fdbc6cdbbe9cd5146
- https://git.kernel.org/stable/c/3b4c70c40f2e135a50cd38fc61c7d23a296a9981
- https://git.kernel.org/stable/c/48067b2ae4504500a7093d9e1e16b42e70330480
- https://git.kernel.org/stable/c/86aa79b43e5b561fd3648891165bd7313b541315
- https://git.kernel.org/stable/c/a82fc217cb7a447313c76ebf9f09b100771b0ddf
- https://git.kernel.org/stable/c/d755cd001fa2c248e186c1fc3df3d11d97dc843c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80600.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80600
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
