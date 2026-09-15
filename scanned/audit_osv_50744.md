# [M] CVE-2020-36778

## Summary
Severity: Medium
Advisory: CVE-2020-36778
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2020-36778
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: xiic: fix reference leak when pm_runtime_get_sync fails

The PM reference count is not expected to be incremented on
return in xiic_xfer and xiic_i2c_remove.

However, pm_runtime_get_sync will increment the PM reference
count even failed. Forgetting to putting operation will result
in a reference leak here.

Replace it with pm_runtime_resume_and_get to keep usage
counter balanced.

## References
- https://git.kernel.org/stable/c/e2ba996577eaea423694dc69ae43d56f1410a22b
- https://git.kernel.org/stable/c/a42ac16e6573f19c78f556ea292f5b534fcc4514
- https://git.kernel.org/stable/c/a85c5c7a3aa8041777ff691400b4046e56149fd3
- https://git.kernel.org/stable/c/c977426db644ba476938125597947979e8aba725
