# [M] CVE-2020-36790

## Summary
Severity: Medium
Advisory: CVE-2020-36790
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2020-36790
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet: fix a memory leak

We forgot to free new_model_number

## References
- https://git.kernel.org/stable/c/227064b2ca9e62270ed445665ae849c73f0dfb2c
- https://git.kernel.org/stable/c/382fee1a8b623e2546a3e15e80517389e0e0673e
