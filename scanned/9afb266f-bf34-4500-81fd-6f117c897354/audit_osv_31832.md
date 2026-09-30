# [H] bpf: Fix softlockup in arena_map_free on 64k page kernel

## Summary
Severity: High
Advisory: CVE-2025-21851
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21851
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix softlockup in arena_map_free on 64k page kernel

On an aarch64 kernel with CONFIG_PAGE_SIZE_64KB=y,
arena_htab tests cause a segmentation fault and soft lockup.
The same failure is not observed with 4k pages on aarch64.

It turns out arena_map_free() is calling
apply_to_existing_page_range() with the address returned by
bpf_arena_get_kern_vm_start().  If this address is not page-aligned
the code ends up calling apply_to_pte_range() with that unaligned
address causing soft lockup.

Fix it by round up GUARD_SZ to PAGE_SIZE << 1 so that the
division by 2 in bpf_arena_get_kern_vm_start() returns
a page-aligned value.

## References
- https://git.kernel.org/stable/c/517e8a7835e8cfb398a0aeb0133de50e31cae32b
- https://git.kernel.org/stable/c/787d556a3de447e70964a4bdeba9196f62a62b1e
- https://git.kernel.org/stable/c/c1f3f3892d4526f18aaeffdb6068ce861e793ee3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21851.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21851
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
