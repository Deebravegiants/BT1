# [M] CVE-2021-47134

## Summary
Severity: Medium
Advisory: CVE-2021-47134
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47134
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

efi/fdt: fix panic when no valid fdt found

setup_arch() would invoke efi_init()->efi_get_fdt_params(). If no
valid fdt found then initial_boot_params will be null. So we
should stop further fdt processing here. I encountered this
issue on risc-v.

## References
- https://git.kernel.org/stable/c/5148066edbdc89c6fe5bc419c31a5c22e5f83bdb
- https://git.kernel.org/stable/c/668a84c1bfb2b3fd5a10847825a854d63fac7baa
- https://git.kernel.org/stable/c/8a7e8b4e5631a03ea2fee27957857a56612108ca
