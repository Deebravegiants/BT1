# [M] CVE-2024-56738

## Summary
Severity: Medium
Advisory: CVE-2024-56738
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56738
Type: osv

## Details
GNU GRUB (aka GRUB2) through 2.12 does not use a constant-time algorithm for grub_crypto_memcmp and thus allows side-channel attacks.

## References
- https://savannah.gnu.org/bugs/?66603
