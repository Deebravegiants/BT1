# [H] CVE-2021-32078

## Summary
Severity: High
Advisory: CVE-2021-32078
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-06-17
Source: https://osv.dev/vulnerability/CVE-2021-32078
Type: osv

## Details
An Out-of-Bounds Read was discovered in arch/arm/mach-footbridge/personal-pci.c in the Linux kernel through 5.12.11 because of the lack of a check for a value that shouldn't be negative, e.g., access to element -2 of an array, aka CID-298a58e165e4.

## References
- https://security.netapp.com/advisory/ntap-20210813-0002/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=298a58e165e447ccfaae35fe9f651f9d7e15166f
- https://github.com/torvalds/linux/commit/298a58e165e447ccfaae35fe9f651f9d7e15166f
- https://kirtikumarar.com/CVE-2021-32078.txt
