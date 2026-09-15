# [M] CVE-2021-47556

## Summary
Severity: Medium
Advisory: CVE-2021-47556
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47556
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ethtool: ioctl: fix potential NULL deref in ethtool_set_coalesce()

ethtool_set_coalesce() now uses both the .get_coalesce() and
.set_coalesce() callbacks. But the check for their availability is
buggy, so changing the coalesce settings on a device where the driver
provides only _one_ of the callbacks results in a NULL pointer
dereference instead of an -EOPNOTSUPP.

Fix the condition so that the availability of both callbacks is
ensured. This also matches the netlink code.

Note that reproducing this requires some effort - it only affects the
legacy ioctl path, and needs a specific combination of driver options:
- have .get_coalesce() and .coalesce_supported but no
 .set_coalesce(), or
- have .set_coalesce() but no .get_coalesce(). Here eg. ethtool doesn't
  cause the crash as it first attempts to call ethtool_get_coalesce()
  and bails out on error.

## References
- https://git.kernel.org/stable/c/abfdd9e2f0f9699015d72317f74154d3e53664e6
- https://git.kernel.org/stable/c/0276af2176c78771da7f311621a25d7608045827
