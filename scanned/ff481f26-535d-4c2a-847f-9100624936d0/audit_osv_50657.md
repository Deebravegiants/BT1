# [M] CVE-2020-27194

## Summary
Severity: Medium
Advisory: CVE-2020-27194
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-16
Source: https://osv.dev/vulnerability/CVE-2020-27194
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.8.15. scalar32_min_max_or in kernel/bpf/verifier.c mishandles bounds tracking during use of 64-bit values, aka CID-5b9fbeb75b6a.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.15
- https://github.com/torvalds/linux/commit/5b9fbeb75b6a98955f628e205ac26689bcb1383e
