# [M] CVE-2021-47143

## Summary
Severity: Medium
Advisory: CVE-2021-47143
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47143
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: remove device from smcd_dev_list after failed device_add()

If the device_add() for a smcd_dev fails, there's no cleanup step that
rolls back the earlier list_add(). The device subsequently gets freed,
and we end up with a corrupted list.

Add some error handling that removes the device from the list.

## References
- https://git.kernel.org/stable/c/40588782f1016c655ae1d302892f61d35af96842
- https://git.kernel.org/stable/c/444d7be9532dcfda8e0385226c862fd7e986f607
- https://git.kernel.org/stable/c/8b2cdc004d21a7255f219706dca64411108f7897
