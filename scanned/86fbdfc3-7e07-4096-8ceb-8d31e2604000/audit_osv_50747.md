# [M] CVE-2020-36781

## Summary
Severity: Medium
Advisory: CVE-2020-36781
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2020-36781
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: imx: fix reference leak when pm_runtime_get_sync fails

In i2c_imx_xfer() and i2c_imx_remove(), the pm reference count
is not expected to be incremented on return.

However, pm_runtime_get_sync will increment pm reference count
even failed. Forgetting to putting operation will result in a
reference leak here.

Replace it with pm_runtime_resume_and_get to keep usage
counter balanced.

## References
- https://git.kernel.org/stable/c/1ecc0ebc2ebbad4a22a670a07d27a21fa0b59c77
- https://git.kernel.org/stable/c/3a0cdd336d92c429b51a79bf4f64b17eafa0325d
- https://git.kernel.org/stable/c/47ff617217ca6a13194fcb35c6c3a0c57c080693
- https://git.kernel.org/stable/c/ff406f6cd09c273337ab4854292e4aca48f8affd
