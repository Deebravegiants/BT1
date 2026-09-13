# [M] drm/amd/display: Fix null check for pipe_ctx->plane_state in hwss_setup_dpp

## Summary
Severity: Medium
Advisory: CVE-2024-53200
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53200
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix null check for pipe_ctx->plane_state in hwss_setup_dpp

This commit addresses a null pointer dereference issue in
hwss_setup_dpp(). The issue could occur when pipe_ctx->plane_state is
null. The fix adds a check to ensure `pipe_ctx->plane_state` is not null
before accessing. This prevents a null pointer dereference.

## References
- https://git.kernel.org/stable/c/020002c76147ecfdafe95c44abd3240e216b6316
- https://git.kernel.org/stable/c/0dd3d1de7a5957804ccd58c1b252f9e34710e3f6
- https://git.kernel.org/stable/c/2bc96c95070571c6c824e0d4c7783bee25a37876
- https://git.kernel.org/stable/c/95792a18da0795300e15075ac05d1915e9066999
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53200.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53200
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
