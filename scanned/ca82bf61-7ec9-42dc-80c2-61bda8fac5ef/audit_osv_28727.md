# [H] riscv: Fix loading 64-bit NOMMU kernels past the start of RAM

## Summary
Severity: High
Advisory: CVE-2024-35987
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35987
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: Fix loading 64-bit NOMMU kernels past the start of RAM

commit 3335068f8721 ("riscv: Use PUD/P4D/PGD pages for the linear
mapping") added logic to allow using RAM below the kernel load address.
However, this does not work for NOMMU, where PAGE_OFFSET is fixed to the
kernel load address. Since that range of memory corresponds to PFNs
below ARCH_PFN_OFFSET, mm initialization runs off the beginning of
mem_map and corrupts adjacent kernel memory. Fix this by restoring the
previous behavior for NOMMU kernels.

## References
- https://git.kernel.org/stable/c/aea702dde7e9876fb00571a2602f25130847bf0f
- https://git.kernel.org/stable/c/b008e327fa570aca210f98c817757649bae56694
- https://git.kernel.org/stable/c/ea6628e4e2353978af7e3b4ad4fdaab6149acf3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35987.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35987
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
