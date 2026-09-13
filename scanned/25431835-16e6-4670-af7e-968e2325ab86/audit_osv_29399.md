# [H] drm/client: Fix error code in drm_client_buffer_vmap_local()

## Summary
Severity: High
Advisory: CVE-2024-42275
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42275
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.10.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/client: Fix error code in drm_client_buffer_vmap_local()

This function accidentally returns zero/success on the failure path.
It leads to locking issues and an uninitialized *map_copy in the
caller.

## References
- https://git.kernel.org/stable/c/b5fbf924f125ba3638cfdc21c0515eb7e76264ca
- https://git.kernel.org/stable/c/c0f412961653237f52e2f16ee8747fb330bcf074
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42275.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42275
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
