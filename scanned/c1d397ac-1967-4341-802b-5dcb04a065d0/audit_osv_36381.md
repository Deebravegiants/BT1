# [H] netfilter: nf_tables: always walk all pending catchall elements

## Summary
Severity: High
Advisory: CVE-2026-23278
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-23278
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.177, >=6.2.0 <6.6.144, >=6.4.0 <6.12.78, >=6.7.0 <6.18.19, >=6.13.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: always walk all pending catchall elements

During transaction processing we might have more than one catchall element:
1 live catchall element and 1 pending element that is coming as part of the
new batch.

If the map holding the catchall elements is also going away, its
required to toggle all catchall elements and not just the first viable
candidate.

Otherwise, we get:
 WARNING: ./include/net/netfilter/nf_tables.h:1281 at nft_data_release+0xb7/0xe0 [nf_tables], CPU#2: nft/1404
 RIP: 0010:nft_data_release+0xb7/0xe0 [nf_tables]
 [..]
 __nft_set_elem_destroy+0x106/0x380 [nf_tables]
 nf_tables_abort_release+0x348/0x8d0 [nf_tables]
 nf_tables_abort+0xcf2/0x3ac0 [nf_tables]
 nfnetlink_rcv_batch+0x9c9/0x20e0 [..]

## References
- https://git.kernel.org/stable/c/4830fb44d12f586f3f544609e086933649a9175a
- https://git.kernel.org/stable/c/77c26b5056d693ffe5e9f040e946251cdb55ae55
- https://git.kernel.org/stable/c/7cb9a23d7ae40a702577d3d8bacb7026f04ac2a9
- https://git.kernel.org/stable/c/c4d4e86fda707d89eaba80e343321737375f8582
- https://git.kernel.org/stable/c/de47a88c6b807910f05703fb6605f7efdaa11417
- https://git.kernel.org/stable/c/eb0948fa13298212c5f8b30ee48efdae4389ab09
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23278.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23278
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
