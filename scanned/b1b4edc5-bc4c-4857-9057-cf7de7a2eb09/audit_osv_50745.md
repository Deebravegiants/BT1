# [M] CVE-2020-36779

## Summary
Severity: Medium
Advisory: CVE-2020-36779
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2020-36779
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: stm32f7: fix reference leak when pm_runtime_get_sync fails

The PM reference count is not expected to be incremented on
return in these stm32f7_i2c_xx serious functions.

However, pm_runtime_get_sync will increment the PM reference
count even failed. Forgetting to putting operation will result
in a reference leak here.

Replace it with pm_runtime_resume_and_get to keep usage
counter balanced.

## References
- https://git.kernel.org/stable/c/2c662660ce2bd3b09dae21a9a9ac9395e1e6c00b
- https://git.kernel.org/stable/c/c323b270a52a26aa8038a4d1fd9a850904a41166
- https://git.kernel.org/stable/c/c7ea772c9fcf711ed566814b92eecaffc0e2bfd0
- https://git.kernel.org/stable/c/d791b90f5c5e5aa8ccf9e33386c16bd2b7e333a4
