# [H] fs/ntfs3: bound NTFS_DE view.data_off in UpdateRecordData{Root,Allocation}

## Summary
Severity: High
Advisory: CVE-2026-64532
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64532
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: bound NTFS_DE view.data_off in UpdateRecordData{Root,Allocation}

In do_action()'s UpdateRecordDataRoot (fslog.c:3489) and
UpdateRecordDataAllocation (fslog.c:3697) cases, the memmove
destination is `Add2Ptr(e, le16_to_cpu(e->view.data_off))`,
where e->view.data_off comes from an on-disk NTFS_DE inside
an INDEX_ROOT or INDEX_BUFFER.  Neither case validates
view.data_off + dlen against e->size; the existing
check_if_index_root / check_if_alloc_index helpers walk the
entry chain and validate the entry's offset, but not its
internal view fields.

The neighbouring read sites (e.g., fs/ntfs3/index.c when
iterating view entries) check view.data_off + view.data_size
<= e->size.  Apply the same bound at the two memmove sites.

Reproduced under UML+KASAN on mainline 8d90b09e6741 via
pr_warn-only probe instrumentation: with view.data_off forced
to 0xFFFC, the memmove writes 32 bytes past the end of the
NTFS_DE.

This is similar in shape to Pavitra Jha's 2026-05-02 patch
"fs/ntfs3: prevent oob in case UpdateRecordDataRoot"
(<20260502105008.21827-1-jhapavitra98@gmail.com>) which
proposes calling ntfs3_bad_de_range(); that helper does not
exist in mainline.  This patch uses inline checks.

## References
- https://git.kernel.org/stable/c/315d3a9a48b49f889da3d858a9307e677cb9e1bd
- https://git.kernel.org/stable/c/36feda687afebae24c472202694448738809c411
- https://git.kernel.org/stable/c/3e127829e57f5190f612412ece4541cb96d5ec7a
- https://git.kernel.org/stable/c/429d653ca641d38a78609b8f62e81a0a5c780a2d
- https://git.kernel.org/stable/c/b20e5a709d8bd190d6e4645606763c7423e694c1
- https://git.kernel.org/stable/c/be306b8d9143a9c076c804a7ca025d69caf9c448
- https://git.kernel.org/stable/c/d41b382068ca4e64e421f736cdd700095464b6ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64532.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64532
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
