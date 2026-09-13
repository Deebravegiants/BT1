# [M] CVE-2021-47053

## Summary
Severity: Medium
Advisory: CVE-2021-47053
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47053
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: sun8i-ss - Fix memory leak of pad

It appears there are several failure return paths that don't seem
to be free'ing pad. Fix these.

Addresses-Coverity: ("Resource leak")

## References
- https://git.kernel.org/stable/c/2c67a9333da9d0a3b87310e0d116b7c9070c7b00
- https://git.kernel.org/stable/c/50274b01ac1689b1a3f6bc4b5b3dbf361a55dd3a
- https://git.kernel.org/stable/c/c633e025bd04f54d7b33331cfcdb71354b08ce59
- https://git.kernel.org/stable/c/d3d702084d125689edb2b9395c707e09b471352e
