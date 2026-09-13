# [M] CVE-2021-47305

## Summary
Severity: Medium
Advisory: CVE-2021-47305
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47305
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

dma-buf/sync_file: Don't leak fences on merge failure

Each add_fence() call does a dma_fence_get() on the relevant fence.  In
the error path, we weren't calling dma_fence_put() so all those fences
got leaked.  Also, in the krealloc_array failure case, we weren't
freeing the fences array.  Instead, ensure that i and fences are always
zero-initialized and dma_fence_put() all the fences and kfree(fences) on
every error path.

## References
- https://git.kernel.org/stable/c/ffe000217c5068c5da07ccb1c0f8cce7ad767435
- https://git.kernel.org/stable/c/0d514185ae792d3a1903c8e1a83899aa996705ce
- https://git.kernel.org/stable/c/19edcd97727aae9362444a859a24d99a8730cb27
- https://git.kernel.org/stable/c/19f51c2529339280d2c8c6427cd3e21ddf1ac3f8
- https://git.kernel.org/stable/c/41f45e91c92c8480242ea448d54e28c753b13902
- https://git.kernel.org/stable/c/e0355a0ad31a1d677b2a4514206de4902bd550e8
