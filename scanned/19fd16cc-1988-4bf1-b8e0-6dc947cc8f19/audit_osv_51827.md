# [M] CVE-2021-4148

## Summary
Severity: Medium
Advisory: CVE-2021-4148
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-23
Source: https://osv.dev/vulnerability/CVE-2021-4148
Type: osv

## Details
A vulnerability was found in the Linux kernel's block_invalidatepage in fs/buffer.c in the filesystem. A missing sanity check may allow a local attacker with user privilege to cause a denial of service (DOS) problem.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2026487
- https://lkml.org/lkml/2021/9/12/323
- https://lkml.org/lkml/2021/9/17/1037
