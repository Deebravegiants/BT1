# [M] CVE-2021-47513

## Summary
Severity: Medium
Advisory: CVE-2021-47513
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47513
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: felix: Fix memory leak in felix_setup_mmio_filtering

Avoid a memory leak if there is not a CPU port defined.

Addresses-Coverity-ID: 1492897 ("Resource leak")
Addresses-Coverity-ID: 1492899 ("Resource leak")

## References
- https://git.kernel.org/stable/c/973a0373e88cc19129bd6ef0ec193040535397d9
- https://git.kernel.org/stable/c/e8b1d7698038e76363859fb47ae0a262080646f5
