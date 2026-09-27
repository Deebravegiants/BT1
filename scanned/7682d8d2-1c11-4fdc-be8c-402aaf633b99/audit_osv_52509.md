# [M] CVE-2021-47524

## Summary
Severity: Medium
Advisory: CVE-2021-47524
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47524
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

serial: liteuart: fix minor-number leak on probe errors

Make sure to release the allocated minor number before returning on
probe errors.

## References
- https://git.kernel.org/stable/c/888fc81107cacd2a4f681bac7bb785cef868214f
- https://git.kernel.org/stable/c/dd5e90b16cca8a697cbe17b72e2a5f49291cabb2
