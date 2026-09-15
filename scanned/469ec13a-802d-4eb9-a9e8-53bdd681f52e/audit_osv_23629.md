# [M] ASoC: atmel: Fix error handling in sam9x5_wm8731_driver_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49241
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49241
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: atmel: Fix error handling in sam9x5_wm8731_driver_probe

The device_node pointer is returned by of_parse_phandle()  with refcount
incremented. We should use of_node_put() on it when done.

This function only calls of_node_put() in the regular path.
And it will cause refcount leak in error path.

## References
- https://git.kernel.org/stable/c/14228225091a0854b1de23e5b4fe8bdeeca9683b
- https://git.kernel.org/stable/c/740dc3e846537c3743da98bf106f376023fd085c
- https://git.kernel.org/stable/c/90ac679aa6a01841da90ec5a4aaa4b5e0badddf0
- https://git.kernel.org/stable/c/f43ad5dc43240289f4cf13c16cc506f4f7087931
- https://git.kernel.org/stable/c/f589063b585ac6dd2081bde6c145411cf48d8d92
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49241.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49241
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
