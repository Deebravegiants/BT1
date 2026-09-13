# [M] CVE-2020-36310

## Summary
Severity: Medium
Advisory: CVE-2020-36310
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-07
Source: https://osv.dev/vulnerability/CVE-2020-36310
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.8. arch/x86/kvm/svm/svm.c allows a set_memory_region_test infinite loop for certain nested page faults, aka CID-e72436bc3a52.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e72436bc3a5206f95bb384e741154166ddb3202e
- https://www.debian.org/security/2022/dsa-5095
