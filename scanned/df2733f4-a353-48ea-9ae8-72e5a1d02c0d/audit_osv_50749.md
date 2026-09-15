# [M] CVE-2020-36783

## Summary
Severity: Medium
Advisory: CVE-2020-36783
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2020-36783
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: img-scb: fix reference leak when pm_runtime_get_sync fails

The PM reference count is not expected to be incremented on
return in functions img_i2c_xfer and img_i2c_init.

However, pm_runtime_get_sync will increment the PM reference
count even failed. Forgetting to putting operation will result
in a reference leak here.

Replace it with pm_runtime_resume_and_get to keep usage
counter balanced.

## References
- https://git.kernel.org/stable/c/7ee35cde1e810ad6ca589980b9ec2b7b62946a5b
- https://git.kernel.org/stable/c/96c4a03658d661666c360959aa80cdabfe2972ed
- https://git.kernel.org/stable/c/e80ae8bde41266d3b8bf012460b6593851766006
- https://git.kernel.org/stable/c/223125e37af8a641ea4a09747a6a52172fc4b903
- https://git.kernel.org/stable/c/4734c4b1d9573c9d20bbc46cf37dde095ee011b8
