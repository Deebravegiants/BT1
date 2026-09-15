# [M] CVE-2017-18551

## Summary
Severity: Medium
Advisory: CVE-2017-18551
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2017-18551
Type: osv

## Details
An issue was discovered in drivers/i2c/i2c-core-smbus.c in the Linux kernel before 4.14.15. There is an out of bounds write in the function i2c_smbus_xfer_emulated.

## References
- https://support.f5.com/csp/article/K48073202?utm_source=f5support&amp%3Butm_medium=RSS
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.15
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=89c6efa61f5709327ecfa24bff18e57a4e80c7fa
