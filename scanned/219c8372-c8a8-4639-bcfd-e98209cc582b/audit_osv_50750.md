# [M] CVE-2020-36784

## Summary
Severity: Medium
Advisory: CVE-2020-36784
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2020-36784
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: cadence: fix reference leak when pm_runtime_get_sync fails

The PM reference count is not expected to be incremented on
return in functions cdns_i2c_master_xfer and cdns_reg_slave.

However, pm_runtime_get_sync will increment pm usage counter
even failed. Forgetting to putting operation will result in a
reference leak here.

Replace it with pm_runtime_resume_and_get to keep usage
counter balanced.

## References
- https://git.kernel.org/stable/c/23ceb8462dc6f4b4decdb5536a7e5fc477cdf0b6
- https://git.kernel.org/stable/c/30410519328c94367e561fd878e5f0d3a0303585
- https://git.kernel.org/stable/c/a45fc41beed8e0fe31864619c34aa00797fb60c1
- https://git.kernel.org/stable/c/d57ff04e0ed6f3be1682ae861ead33f879225e07
