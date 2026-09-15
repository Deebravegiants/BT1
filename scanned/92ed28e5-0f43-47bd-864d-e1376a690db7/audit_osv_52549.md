# [M] CVE-2021-47567

## Summary
Severity: Medium
Advisory: CVE-2021-47567
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47567
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/32: Fix hardlockup on vmap stack overflow

Since the commit c118c7303ad5 ("powerpc/32: Fix vmap stack - Do not
activate MMU before reading task struct") a vmap stack overflow
results in a hard lockup. This is because emergency_ctx is still
addressed with its virtual address allthough data MMU is not active
anymore at that time.

Fix it by using a physical address instead.

## References
- https://git.kernel.org/stable/c/dfe906da9a1abebdebe8b15bb3e66a2578f6c4c7
- https://git.kernel.org/stable/c/5bb60ea611db1e04814426ed4bd1c95d1487678e
- https://git.kernel.org/stable/c/c4e3ff8b8b1d54f0c755670174c453b06e17114b
