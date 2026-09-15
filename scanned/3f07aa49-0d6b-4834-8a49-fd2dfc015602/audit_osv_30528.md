# [M] drm/vmwgfx: avoid null_ptr_deref in vmw_framebuffer_surface_create_handle

## Summary
Severity: Medium
Advisory: CVE-2024-53115
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53115
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: avoid null_ptr_deref in vmw_framebuffer_surface_create_handle

The 'vmw_user_object_buffer' function may return NULL with incorrect
inputs. To avoid possible null pointer dereference, add a check whether
the 'bo' is NULL in the vmw_framebuffer_surface_create_handle.

## References
- https://git.kernel.org/stable/c/36f64da080555175b58d85f99f5f90435e274e56
- https://git.kernel.org/stable/c/93d1f41a82de382845af460bf03bcb17dcbf08c5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53115.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53115
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
