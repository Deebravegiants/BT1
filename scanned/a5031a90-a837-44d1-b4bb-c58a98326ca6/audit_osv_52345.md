# [H] CVE-2021-47352

## Summary
Severity: High
Advisory: CVE-2021-47352
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47352
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio-net: Add validation for used length

This adds validation for used length (might come
from an untrusted device) to avoid data corruption
or loss.

## References
- https://git.kernel.org/stable/c/3133e01514c3c498f2b01ff210ee6134b70c663c
- https://git.kernel.org/stable/c/ad993a95c508417acdeb15244109e009e50d8758
- https://git.kernel.org/stable/c/ba710baa1cc1b17a0483f7befe03e696efd17292
- https://git.kernel.org/stable/c/c1b40d1959517ff2ea473d40eeab4691d6d62462
- https://git.kernel.org/stable/c/c92298d228f61589dd21657af2bea95fc866b813
