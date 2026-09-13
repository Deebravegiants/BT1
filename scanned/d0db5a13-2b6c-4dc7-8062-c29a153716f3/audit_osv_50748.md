# [M] CVE-2020-36782

## Summary
Severity: Medium
Advisory: CVE-2020-36782
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2020-36782
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: imx-lpi2c: fix reference leak when pm_runtime_get_sync fails

The PM reference count is not expected to be incremented on
return in lpi2c_imx_master_enable.

However, pm_runtime_get_sync will increment the PM reference
count even failed. Forgetting to putting operation will result
in a reference leak here.

Replace it with pm_runtime_resume_and_get to keep usage
counter balanced.

## References
- https://git.kernel.org/stable/c/b100650d80cd2292f6c152f5f2943b5944b3e8ce
- https://git.kernel.org/stable/c/bb300acc867e937edc2a6898e92b21f88e4e4e66
- https://git.kernel.org/stable/c/cc49d206414240483bb93ffa3d80243e6a776916
- https://git.kernel.org/stable/c/278e5bbdb9a94fa063c0f9bcde2479d0b8042462
- https://git.kernel.org/stable/c/815859cb1d2302e74f11bf6894bceace9ca9eb4a
