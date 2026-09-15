# [H] netfilter: nf_tables: Fix potential data-race in __nft_obj_type_get()

## Summary
Severity: High
Advisory: CVE-2024-27019
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27019
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.219, >=5.11.0 <5.15.157, >=5.16.0 <6.1.88, >=6.2.0 <6.6.29, >=6.7.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: Fix potential data-race in __nft_obj_type_get()

nft_unregister_obj() can concurrent with __nft_obj_type_get(),
and there is not any protection when iterate over nf_tables_objects
list in __nft_obj_type_get(). Therefore, there is potential data-race
of nf_tables_objects list entry.

Use list_for_each_entry_rcu() to iterate over nf_tables_objects
list in __nft_obj_type_get(), and use rcu_read_lock() in the caller
nft_obj_type_get() to protect the entire type query process.

## References
- https://git.kernel.org/stable/c/379bf7257bc5f2a1b1ca8514e08a871b7bf6d920
- https://git.kernel.org/stable/c/4ca946b19caf655a08d5e2266d4d5526025ebb73
- https://git.kernel.org/stable/c/ad333578f736d56920e090d7db1f8dec891d815e
- https://git.kernel.org/stable/c/cade34279c2249eafe528564bd2e203e4ff15f88
- https://git.kernel.org/stable/c/d78d867dcea69c328db30df665be5be7d0148484
- https://git.kernel.org/stable/c/df7c0fb8c2b9f9cac65659332581b19682a71349
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27019.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27019
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
