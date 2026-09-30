# [C] ipvs: reset full ip_vs_seq structs in ip_vs_conn_new

## Summary
Severity: Critical
Advisory: CVE-2026-72020
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72020
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: reset full ip_vs_seq structs in ip_vs_conn_new

Commit 9a05475cebdd ("ipvs: avoid kmem_cache_zalloc in
ip_vs_conn_new") changed ip_vs_conn_new() to allocate an ip_vs_conn
object with kmem_cache_alloc().  The function then initializes many
fields explicitly, but only resets in_seq.delta and out_seq.delta in the
two struct ip_vs_seq members.

That leaves init_seq and previous_delta uninitialized.  This is normally
harmless while the corresponding IP_VS_CONN_F_IN_SEQ or
IP_VS_CONN_F_OUT_SEQ flag is clear.  For connections learned from a sync
message, however, ip_vs_proc_conn() preserves those flags from
IP_VS_CONN_F_BACKUP_MASK and passes opt=NULL when the message omits
IPVS_OPT_SEQ_DATA.  In that case the new connection can be hashed with
SEQ flags set but with the rest of in_seq/out_seq still containing stale
slab data.

When a packet for such a connection is later handled by an IPVS
application helper, vs_fix_seq() and vs_fix_ack_seq() use
previous_delta and init_seq to rewrite TCP sequence numbers.  A malformed
sync message can therefore make forwarded packets carry stale slab bytes
in their TCP seq/ack numbers, and can also corrupt the forwarded TCP
flow.

Reset both struct ip_vs_seq members completely before publishing the
connection.  This matches the existing "reset struct ip_vs_seq" comment
and keeps the sequence-adjustment gates inactive unless valid sequence
data is installed later.

## References
- https://git.kernel.org/stable/c/2975324d164c552b028632f107b567302863b7f6
- https://git.kernel.org/stable/c/32c299e28b8eea6cbbd23b97dc61401e9ef9c445
- https://git.kernel.org/stable/c/3bf9a260188b2a5449cbddc032a749ab433fe328
- https://git.kernel.org/stable/c/6335ab62d5fc9ed875279238233fba3462c168f5
- https://git.kernel.org/stable/c/6378c5cb360eb1750f88839d7c3613ea92ac1816
- https://git.kernel.org/stable/c/83fb4c2c5344f02eac929f66de3c9d1adfcde04c
- https://git.kernel.org/stable/c/9e36602cbec552286f7e691cfd366525c565ee74
- https://git.kernel.org/stable/c/d0eed7177e822cab83141e5c44b2aa345c7fd379
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72020.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72020
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
