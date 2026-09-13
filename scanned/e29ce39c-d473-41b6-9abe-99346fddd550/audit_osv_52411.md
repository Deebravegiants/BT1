# [M] CVE-2021-47420

## Summary
Severity: Medium
Advisory: CVE-2021-47420
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47420
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: fix a potential ttm->sg memory leak

Memory is allocated for ttm->sg by kmalloc in kfd_mem_dmamap_userptr,
but isn't freed by kfree in kfd_mem_dmaunmap_userptr. Free it!

## References
- https://git.kernel.org/stable/c/7e5ce6029b627efb4a004746cfdc1eeff850e6eb
- https://git.kernel.org/stable/c/b072ef1215aca33186e3a10109e872e528a9e516
