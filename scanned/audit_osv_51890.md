# [M] CVE-2021-4453

## Summary
Severity: Medium
Advisory: CVE-2021-4453
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-4453
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/pm: fix a potential gpu_metrics_table memory leak

Memory is allocated for gpu_metrics_table in renoir_init_smc_tables(),
but not freed in int smu_v12_0_fini_smc_tables(). Free it!

## References
- https://git.kernel.org/stable/c/222cebd995cdf11fe0d502749560f65e64990e55
- https://git.kernel.org/stable/c/257b3bb16634fd936129fe2f57a91594a75b8751
- https://git.kernel.org/stable/c/aa464957f7e660abd554f2546a588f6533720e21
