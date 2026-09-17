# [M] CVE-2020-36780

## Summary
Severity: Medium
Advisory: CVE-2020-36780
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2020-36780
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: sprd: fix reference leak when pm_runtime_get_sync fails

The PM reference count is not expected to be incremented on
return in sprd_i2c_master_xfer() and sprd_i2c_remove().

However, pm_runtime_get_sync will increment the PM reference
count even failed. Forgetting to putting operation will result
in a reference leak here.

Replace it with pm_runtime_resume_and_get to keep usage
counter balanced.

## References
- https://git.kernel.org/stable/c/e547640cee7981fd751d2c9cde3a61bdb678b755
- https://git.kernel.org/stable/c/3a4f326463117cee3adcb72999ca34a9aaafda93
- https://git.kernel.org/stable/c/7e1764312440c5df9dfe6b436035a03673b0c1b9
- https://git.kernel.org/stable/c/9223505e938ba3db5907e058f4209770cff2f2a7
- https://git.kernel.org/stable/c/d3406ab52097328a3bc4cbe124bfd8f6d51fb86f
