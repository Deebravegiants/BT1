# [M] CVE-2021-47009

## Summary
Severity: Medium
Advisory: CVE-2021-47009
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47009
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

KEYS: trusted: Fix memory leak on object td

Two error return paths are neglecting to free allocated object td,
causing a memory leak. Fix this by returning via the error return
path that securely kfree's td.

Fixes clang scan-build warning:
security/keys/trusted-keys/trusted_tpm1.c:496:10: warning: Potential
memory leak [unix.Malloc]

## References
- https://git.kernel.org/stable/c/3e24fbd37e72e8a67b74991970fecc82d14f57af
- https://git.kernel.org/stable/c/83a775d5f9bfda95b1c295f95a3a041a40c7f321
- https://git.kernel.org/stable/c/1c4031014106aff48e1e686e40101c31eab5d44c
- https://git.kernel.org/stable/c/31c9a4b24d86cbb36ff0d7a085725a3b4f0138c8
