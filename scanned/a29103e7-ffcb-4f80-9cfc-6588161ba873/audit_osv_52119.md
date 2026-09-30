# [M] CVE-2021-47095

## Summary
Severity: Medium
Advisory: CVE-2021-47095
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47095
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipmi: ssif: initialize ssif_info->client early

During probe ssif_info->client is dereferenced in error path. However,
it is set when some of the error checking has already been done. This
causes following kernel crash if an error path is taken:

[   30.645593][  T674] ipmi_ssif 0-000e: ipmi_ssif: Not probing, Interface already present
[   30.657616][  T674] Unable to handle kernel NULL pointer dereference at virtual address 0000000000000088
...
[   30.657723][  T674] pc : __dev_printk+0x28/0xa0
[   30.657732][  T674] lr : _dev_err+0x7c/0xa0
...
[   30.657772][  T674] Call trace:
[   30.657775][  T674]  __dev_printk+0x28/0xa0
[   30.657778][  T674]  _dev_err+0x7c/0xa0
[   30.657781][  T674]  ssif_probe+0x548/0x900 [ipmi_ssif 62ce4b08badc1458fd896206d9ef69a3c31f3d3e]
[   30.657791][  T674]  i2c_device_probe+0x37c/0x3c0
...

Initialize ssif_info->client before any error path can be taken. Clear
i2c_client data in the error path to prevent the dangling pointer from
leaking.

## References
- https://git.kernel.org/stable/c/1f6ab847461ce7dd89ae9db2dd4658c993355d7c
- https://git.kernel.org/stable/c/34f35f8f14bc406efc06ee4ff73202c6fd245d15
- https://git.kernel.org/stable/c/77a7311ca167aa5b7055c549a940a56e73ee5f29
- https://git.kernel.org/stable/c/8efd6a3391f7b0b19fb0c38e50add06ca30c94af
