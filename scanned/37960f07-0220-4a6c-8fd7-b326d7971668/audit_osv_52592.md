# [H] CVE-2021-47614

## Summary
Severity: High
Advisory: CVE-2021-47614
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47614
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/irdma: Fix a user-after-free in add_pble_prm

When irdma_hmc_sd_one fails, 'chunk' is freed while its still on the PBLE
info list.

Add the chunk entry to the PBLE info list only after successful setting of
the SD in irdma_hmc_sd_one.

## References
- https://git.kernel.org/stable/c/11eebcf63e98fcf047a876a51d76afdabc3b8b9b
- https://git.kernel.org/stable/c/1e11a39a82e95ce86f849f40dda0d9c0498cebd9
