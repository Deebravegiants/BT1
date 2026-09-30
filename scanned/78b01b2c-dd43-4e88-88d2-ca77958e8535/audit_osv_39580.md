# [H] drm/xe: Fix dma-buf attachment leak in xe_gem_prime_import()

## Summary
Severity: High
Advisory: CVE-2026-46201
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46201
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Fix dma-buf attachment leak in xe_gem_prime_import()

When xe_dma_buf_init_obj() fails, the attachment from
dma_buf_dynamic_attach() is not detached. Add dma_buf_detach() before
returning the error. Note: we cannot use goto out_err here because
xe_dma_buf_init_obj() already frees bo on failure, and out_err would
double-free it.

(cherry picked from commit a828eb185aac41800df8eae4b60501ccc0dbbe51)

## References
- https://git.kernel.org/stable/c/0afa8b1ef582ecf6fb04097fd356f8741e5005ed
- https://git.kernel.org/stable/c/111ab678471bf1f90d078d5513bb086b70596c3c
- https://git.kernel.org/stable/c/d394669e194936d7ce15284a24a5ae334c4c5b74
- https://git.kernel.org/stable/c/eea1e10f8d99c0f04deef707c99705b94bba3b78
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46201.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46201
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
