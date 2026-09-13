# [H] CVE-2021-46943

## Summary
Severity: High
Advisory: CVE-2021-46943
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46943
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: staging/intel-ipu3: Fix set_fmt error handling

If there in an error during a set_fmt, do not overwrite the previous
sizes with the invalid config.

Without this patch, v4l2-compliance ends up allocating 4GiB of RAM and
causing the following OOPs

[   38.662975] ipu3-imgu 0000:00:05.0: swiotlb buffer is full (sz: 4096 bytes)
[   38.662980] DMA: Out of SW-IOMMU space for 4096 bytes at device 0000:00:05.0
[   38.663010] general protection fault: 0000 [#1] PREEMPT SMP

## References
- https://git.kernel.org/stable/c/a03fb1e8a110658215a4cefc3e2ad53279e496a6
- https://git.kernel.org/stable/c/ad91849996f9dd79741a961fd03585a683b08356
- https://git.kernel.org/stable/c/c6b81b897f6f9445d57f8d47c4e060ec21556137
- https://git.kernel.org/stable/c/34892ea938387d83ffcfb7775ec55f0f80767916
- https://git.kernel.org/stable/c/6fb617e37a39db0a3eca4489431359d0bdf3b9bc
