# [M] efi: fix potential NULL deref in efi_mem_reserve_persistent

## Summary
Severity: Medium
Advisory: CVE-2023-52976
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52976
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.232, >=5.5.0 <5.10.168, >=5.11.0 <5.15.93, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

efi: fix potential NULL deref in efi_mem_reserve_persistent

When iterating on a linked list, a result of memremap is dereferenced
without checking it for NULL.

This patch adds a check that falls back on allocating a new page in
case memremap doesn't succeed.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

[ardb: return -ENOMEM instead of breaking out of the loop]

## References
- https://git.kernel.org/stable/c/87d4ff18738fd71e7e3c10827c80257da6283697
- https://git.kernel.org/stable/c/966d47e1f27c45507c5df82b2a2157e5a4fd3909
- https://git.kernel.org/stable/c/a2e6a9ff89f13666a1c3ff7195612ab949ea9afc
- https://git.kernel.org/stable/c/d8fc0b5fb3e816a4a8684bcd3ed02cbef0fce23c
- https://git.kernel.org/stable/c/d92a25627bcdf264183670da73c9a60c0bac327e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52976.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52976
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
