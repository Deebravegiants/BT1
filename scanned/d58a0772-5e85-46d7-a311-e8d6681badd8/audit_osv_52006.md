# [M] CVE-2021-46953

## Summary
Severity: Medium
Advisory: CVE-2021-46953
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46953
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPI: GTDT: Don't corrupt interrupt mappings on watchdow probe failure

When failing the driver probe because of invalid firmware properties,
the GTDT driver unmaps the interrupt that it mapped earlier.

However, it never checks whether the mapping of the interrupt actially
succeeded. Even more, should the firmware report an illegal interrupt
number that overlaps with the GIC SGI range, this can result in an
IPI being unmapped, and subsequent fireworks (as reported by Dann
Frazier).

Rework the driver to have a slightly saner behaviour and actually
check whether the interrupt has been mapped before unmapping things.

## References
- https://git.kernel.org/stable/c/7b2162db1498c71962a4bb2f776fa4e76d4d305b
- https://git.kernel.org/stable/c/c3385a9122f8db15b453e07bfc88117fce7f3724
- https://git.kernel.org/stable/c/e0f2d86481eaa83df33b0793f75212919db7a19d
- https://git.kernel.org/stable/c/1ecd5b129252249b9bc03d7645a7bda512747277
- https://git.kernel.org/stable/c/42e69521ee1fa5abf21f478d147d06bbfe6bf6a8
- https://git.kernel.org/stable/c/504632a3577a049dd9bb7aabae5b4476f9c586b4
- https://git.kernel.org/stable/c/596e079c362ac17ed02aa1b99fdc444d62072a01
