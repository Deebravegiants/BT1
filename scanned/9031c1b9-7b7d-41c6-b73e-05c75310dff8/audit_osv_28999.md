# [H] drm/mediatek: Init `ddp_comp` with devm_kcalloc()

## Summary
Severity: High
Advisory: CVE-2024-38592
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38592
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/mediatek: Init `ddp_comp` with devm_kcalloc()

In the case where `conn_routes` is true we allocate an extra slot in
the `ddp_comp` array but mtk_drm_crtc_create() never seemed to
initialize it in the test case I ran. For me, this caused a later
crash when we looped through the array in mtk_drm_crtc_mode_valid().
This showed up for me when I booted with `slub_debug=FZPUA` which
poisons the memory initially. Without `slub_debug` I couldn't
reproduce, presumably because the later code handles the value being
NULL and in most cases (not guaranteed in all cases) the memory the
allocator returned started out as 0.

It really doesn't hurt to initialize the array with devm_kcalloc()
since the array is small and the overhead of initting a handful of
elements to 0 is small. In general initting memory to zero is a safer
practice and usually it's suggested to only use the non-initting alloc
functions if you really need to.

Let's switch the function to use an allocation function that zeros the
memory. For me, this avoids the crash.

## References
- https://git.kernel.org/stable/c/01a2c5123e27b3c4685bf2fc4c2e879f6e0c7b33
- https://git.kernel.org/stable/c/9fe2cc3fa44f7ad7ba5f29c1a68b2b924c17b9b1
- https://git.kernel.org/stable/c/cf69d0af7db917b82aceaa44b7b1b9376609da22
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38592.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38592
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
