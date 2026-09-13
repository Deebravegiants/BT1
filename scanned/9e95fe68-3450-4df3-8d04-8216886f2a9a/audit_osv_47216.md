# [H] CVE-2016-10907

## Summary
Severity: High
Advisory: CVE-2016-10907
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-19
Source: https://osv.dev/vulnerability/CVE-2016-10907
Type: osv

## Details
An issue was discovered in drivers/iio/dac/ad5755.c in the Linux kernel before 4.8.6. There is an out of bounds write in the function ad5755_parse_dt.

## References
- https://support.f5.com/csp/article/K79609038
- https://support.f5.com/csp/article/K79609038?utm_source=f5support&amp%3Butm_medium=RSS
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.6
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9d47964bfd471f0dd4c89f28556aec68bffa0020
