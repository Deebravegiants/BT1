# [M] CVE-2021-47258

## Summary
Severity: Medium
Advisory: CVE-2021-47258
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47258
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: core: Fix error handling of scsi_host_alloc()

After device is initialized via device_initialize(), or its name is set via
dev_set_name(), the device has to be freed via put_device().  Otherwise
device name will be leaked because it is allocated dynamically in
dev_set_name().

Fix the leak by replacing kfree() with put_device(). Since
scsi_host_dev_release() properly handles IDA and kthread removal, remove
special-casing these from the error handling as well.

## References
- https://git.kernel.org/stable/c/45d83db4728127944b237c0c8248987df9d478e7
- https://git.kernel.org/stable/c/66a834d092930cf41d809c0e989b13cd6f9ca006
- https://git.kernel.org/stable/c/79296e292d67fa7b5fb8d8c27343683e823872c8
- https://git.kernel.org/stable/c/7a696ce1d5d16a33a6cd6400bbcc0339b2460e11
- https://git.kernel.org/stable/c/8958181c1663e24a13434448e7d6b96b5d04900a
- https://git.kernel.org/stable/c/db08ce595dd64ea9859f7d088b51cbfc8e685c66
- https://git.kernel.org/stable/c/2dc85045ae65b9302a1d2e2ddd7ce4c030153a6a
