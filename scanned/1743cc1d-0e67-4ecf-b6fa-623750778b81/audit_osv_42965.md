# [C] batman-adv: access unicast_ttvn skb->data only after skb realloc

## Summary
Severity: Critical
Advisory: CVE-2026-72234
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72234
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: access unicast_ttvn skb->data only after skb realloc

The pskb_may_pull() called by batadv_get_vid() could reallocate the buffer
behind the skb. Variables which were pointing to the old buffer need to be
reassigned to avoid an use-after-free.

This was done correctly for the ethernet header but missed for the
unicast_packet pointer.

## References
- https://git.kernel.org/stable/c/7141990add3f75436f2933cb310654cad3b1e3e9
- https://git.kernel.org/stable/c/7b162b36de750565404cd3b98315706622c6974f
- https://git.kernel.org/stable/c/979175834a699ccc3c4c0b0ba60ecae0f135a587
- https://git.kernel.org/stable/c/9a7b7248798123efbd5fafe58461d57c7cc718af
- https://git.kernel.org/stable/c/9c2c05629e46c1fd43931506d41c56a885a98eb4
- https://git.kernel.org/stable/c/aa9558af859934f24717d4bab97d61004f91a736
- https://git.kernel.org/stable/c/b8afcf799b2cc92c41beebd029e53ed18960184a
- https://git.kernel.org/stable/c/ed90eb5c68420cdfe67ec1f773324198d2ef6f50
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72234.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72234
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
