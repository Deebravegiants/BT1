# [H] CVE-2021-47604

## Summary
Severity: High
Advisory: CVE-2021-47604
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47604
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

vduse: check that offset is within bounds in get_config()

This condition checks "len" but it does not check "offset" and that
could result in an out of bounds read if "offset > dev->config_size".
The problem is that since both variables are unsigned the
"dev->config_size - offset" subtraction would result in a very high
unsigned value.

I think these checks might not be necessary because "len" and "offset"
are supposed to already have been validated using the
vhost_vdpa_config_validate() function.  But I do not know the code
perfectly, and I like to be safe.

## References
- https://git.kernel.org/stable/c/dc1db0060c02d119fd4196924eff2d1129e9a442
- https://git.kernel.org/stable/c/ebbbc5fea3f648175df1aa3f127c78eb0252cc2a
