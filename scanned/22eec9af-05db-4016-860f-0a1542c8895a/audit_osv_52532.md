# [M] CVE-2021-47550

## Summary
Severity: Medium
Advisory: CVE-2021-47550
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47550
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/amdgpu: fix potential memleak

In function amdgpu_get_xgmi_hive, when kobject_init_and_add failed
There is a potential memleak if not call kobject_put.

## References
- https://git.kernel.org/stable/c/27dfaedc0d321b4ea4e10c53e4679d6911ab17aa
- https://git.kernel.org/stable/c/75752ada77e0726327adf68018b9f50ae091baeb
- https://git.kernel.org/stable/c/c746945fb6bcbe3863c9ea6369c7ef376e38e5eb
