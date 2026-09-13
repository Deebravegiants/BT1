# [M] CVE-2021-47648

## Summary
Severity: Medium
Advisory: CVE-2021-47648
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47648
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpu: host1x: Fix a memory leak in 'host1x_remove()'

Add a missing 'host1x_channel_list_free()' call in the remove function,
as already done in the error handling path of the probe function.

## References
- https://git.kernel.org/stable/c/025c6643a81564f066d8381b9e2f4603e0f8438f
- https://git.kernel.org/stable/c/5124a344983e1b9670dae7add0e4d00d589aabcd
- https://git.kernel.org/stable/c/6bb107332db28a0e9256c2d36a0902b85307612c
- https://git.kernel.org/stable/c/c06577a80485511b894cb688e881ef0bc2d1d296
- https://git.kernel.org/stable/c/fe1ce680560d4f0049ffa0c687de17567421c1ec
