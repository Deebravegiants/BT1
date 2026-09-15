# [M] drm/amdgpu: Fix potential NULL pointer dereference in atomctrl_get_smc_sclk_range_table

## Summary
Severity: Medium
Advisory: CVE-2024-58052
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58052
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix potential NULL pointer dereference in atomctrl_get_smc_sclk_range_table

The function atomctrl_get_smc_sclk_range_table() does not check the return
value of smu_atom_get_data_table(). If smu_atom_get_data_table() fails to
retrieve SMU_Info table, it returns NULL which is later dereferenced.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

In practice this should never happen as this code only gets called
on polaris chips and the vbios data table will always be present on
those chips.

## References
- https://git.kernel.org/stable/c/0b97cd8a61b2b40fd73cf92a4bb2256462d22adb
- https://git.kernel.org/stable/c/2396bc91935c6da0588ce07850d07897974bd350
- https://git.kernel.org/stable/c/357445e28ff004d7f10967aa93ddb4bffa5c3688
- https://git.kernel.org/stable/c/396350adf0e5ad4bf05f01e4d79bfb82f0f6c41a
- https://git.kernel.org/stable/c/6a30634a2e0f1dd3c6b39fd0f114c32893a9907a
- https://git.kernel.org/stable/c/a713ba7167c2d74c477dd7764dbbdbe3199f17f4
- https://git.kernel.org/stable/c/ae522ad211ec4b72eaf742b25f24b0a406afcba1
- https://git.kernel.org/stable/c/c47066ed7c8f3b320ef87fa6217a2b8b24e127cc
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58052.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58052
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
