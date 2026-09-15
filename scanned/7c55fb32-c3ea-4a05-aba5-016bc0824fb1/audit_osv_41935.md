# [H] qed: fix double free in qed_cxt_tables_alloc()

## Summary
Severity: High
Advisory: CVE-2026-64118
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64118
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

qed: fix double free in qed_cxt_tables_alloc()

If one of the later PF or VF CID bitmap allocations fails,
qed_cid_map_alloc() jumps to cid_map_fail and frees the previously
allocated CID bitmaps before returning an error. qed_cxt_tables_alloc()
then calls qed_cxt_mngr_free(), which invokes qed_cid_map_free()
again.

Fix this by setting each CID bitmap pointer to NULL after bitmap_free()
to avoid double free.

The bug was first flagged by an experimental analysis tool we are
developing for kernel memory-management bugs while analyzing
v6.13-rc1. The tool is still under development and is not yet publicly
available. Manual inspection confirms that the bug is still
present in v7.1-rc3.

Runtime reproduction was not attempted because exercising the failing
allocation path requires device-specific setup.

## References
- https://git.kernel.org/stable/c/06fa8e69019fd3c41a7b0ea8c5f509c3a33dc227
- https://git.kernel.org/stable/c/0e47fc1c9181ae029e0e35a865cbf2adcbae626c
- https://git.kernel.org/stable/c/2bccfb8476ca5f3548afbd623dc7a6980d4e77de
- https://git.kernel.org/stable/c/3904b993cc17ec5d7c5d3b57dbd0b775dafb9684
- https://git.kernel.org/stable/c/8cf5e4d2ca6b101d163c7423a426fb0aec34f7bb
- https://git.kernel.org/stable/c/9fe030719bd083b766602692ee96c8c985798e3c
- https://git.kernel.org/stable/c/a04c207f0801abdd23a169b5f902a9845059a65a
- https://git.kernel.org/stable/c/bdf678a273cadbccc347f331ae2e93ff4d14834c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64118.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64118
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
