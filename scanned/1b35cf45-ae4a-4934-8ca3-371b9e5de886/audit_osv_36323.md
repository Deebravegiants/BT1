# [H] macvlan: fix possible UAF in macvlan_forward_source()

## Summary
Severity: High
Advisory: CVE-2026-23001
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-25
Source: https://osv.dev/vulnerability/CVE-2026-23001
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.10.249, >=5.11.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.122, >=6.7.0 <6.12.67, >=6.13.0 <6.18.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

macvlan: fix possible UAF in macvlan_forward_source()

Add RCU protection on (struct macvlan_source_entry)->vlan.

Whenever macvlan_hash_del_source() is called, we must clear
entry->vlan pointer before RCU grace period starts.

This allows macvlan_forward_source() to skip over
entries queued for freeing.

Note that macvlan_dev are already RCU protected, as they
are embedded in a standard netdev (netdev_priv(ndev)).

https: //lore.kernel.org/netdev/695fb1e8.050a0220.1c677c.039f.GAE@google.com/T/#u

## References
- https://git.kernel.org/stable/c/15f6faf36e162532bec5cc05eb3fc622108bf2ed
- https://git.kernel.org/stable/c/232afc74a6dde0fe1830988e5827921f5ec9bb3f
- https://git.kernel.org/stable/c/484919832e2db6ce1e8add92c469e5d459a516b5
- https://git.kernel.org/stable/c/6dbead9c7677186f22b7981dd085a0feec1f038e
- https://git.kernel.org/stable/c/7470a7a63dc162f07c26dbf960e41ee1e248d80e
- https://git.kernel.org/stable/c/8133e85b8a3ec9f10d861e0002ec6037256e987e
- https://git.kernel.org/stable/c/8518712a2ca952d6da2238c6f0a16b4ae5ea3f13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23001.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23001
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
