# [M] CVE-2021-38198

## Summary
Severity: Medium
Advisory: CVE-2021-38198
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-08
Source: https://osv.dev/vulnerability/CVE-2021-38198
Type: osv

## Details
arch/x86/kvm/mmu/paging_tmpl.h in the Linux kernel before 5.12.11 incorrectly computes the access permissions of a shadow page, leading to a missing guest protection page fault.

## References
- https://lists.debian.org/debian-lts-announce/2021/10/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://github.com/torvalds/linux/commit/b1bd5cba3306691c771d558e94baa73e8b0b96b7
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.11
