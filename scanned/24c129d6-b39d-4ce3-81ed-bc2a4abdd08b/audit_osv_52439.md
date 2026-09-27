# [M] CVE-2021-47450

## Summary
Severity: Medium
Advisory: CVE-2021-47450
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47450
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Fix host stage-2 PGD refcount

The KVM page-table library refcounts the pages of concatenated stage-2
PGDs individually. However, when running KVM in protected mode, the
host's stage-2 PGD is currently managed by EL2 as a single high-order
compound page, which can cause the refcount of the tail pages to reach 0
when they shouldn't, hence corrupting the page-table.

Fix this by introducing a new hyp_split_page() helper in the EL2 page
allocator (matching the kernel's split_page() function), and make use of
it from host_s2_zalloc_pages_exact().

## References
- https://git.kernel.org/stable/c/1d58a17ef54599506d44c45ac95be27273a4d2b1
- https://git.kernel.org/stable/c/b372264c66ef78f2cab44e877fbd765ad6d24c39
