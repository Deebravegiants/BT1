# [H] CVE-2021-47605

## Summary
Severity: High
Advisory: CVE-2021-47605
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47605
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

vduse: fix memory corruption in vduse_dev_ioctl()

The "config.offset" comes from the user.  There needs to a check to
prevent it being out of bounds.  The "config.offset" and
"dev->config_size" variables are both type u32.  So if the offset if
out of bounds then the "dev->config_size - config.offset" subtraction
results in a very high u32 value.  The out of bounds offset can result
in memory corruption.

## References
- https://git.kernel.org/stable/c/e6c67560b4341914bec32ec536e931c22062af65
- https://git.kernel.org/stable/c/ff9f9c6e74848170fcb45c8403c80d661484c8c9
