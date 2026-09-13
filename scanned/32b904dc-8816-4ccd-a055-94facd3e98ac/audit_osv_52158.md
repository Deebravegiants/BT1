# [M] CVE-2021-47141

## Summary
Severity: Medium
Advisory: CVE-2021-47141
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47141
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

gve: Add NULL pointer checks when freeing irqs.

When freeing notification blocks, we index priv->msix_vectors.
If we failed to allocate priv->msix_vectors (see abort_with_msix_vectors)
this could lead to a NULL pointer dereference if the driver is unloaded.

## References
- https://git.kernel.org/stable/c/821149ee88c206fa37e79c1868cc270518484876
- https://git.kernel.org/stable/c/da21a35c00ff1a1794d4f166d3b3fa8db4d0f6fb
- https://git.kernel.org/stable/c/5218e919c8d06279884aa0baf76778a6817d5b93
- https://git.kernel.org/stable/c/5278c75266c5094d3c0958793bf12fc90300e580
