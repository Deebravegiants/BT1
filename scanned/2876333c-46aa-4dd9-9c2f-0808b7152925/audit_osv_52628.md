# [M] CVE-2021-47658

## Summary
Severity: Medium
Advisory: CVE-2021-47658
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47658
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/pm: fix a potential gpu_metrics_table memory leak

Memory is allocated for gpu_metrics_table in renoir_init_smc_tables(),
but not freed in int smu_v12_0_fini_smc_tables(). Free it!

## References
- https://git.kernel.org/stable/c/583637d66a70fc7090e12fb0ebbacc33d39e2214
