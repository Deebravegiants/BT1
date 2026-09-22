# [H] CVE-2016-7913

## Summary
Severity: High
Advisory: CVE-2016-7913
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2016-7913
Type: osv

## Details
The xc2028_set_config function in drivers/media/tuners/tuner-xc2028.c in the Linux kernel before 4.6 allows local users to gain privileges or cause a denial of service (use-after-free) via vectors involving omission of the firmware name from a certain data structure.

## References
- http://www.securityfocus.com/bid/94201
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/errata/RHSA-2019:1190
- http://source.android.com/security/bulletin/2016-11-01.html
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2019:1170
- https://usn.ubuntu.com/3798-1/
- https://usn.ubuntu.com/3798-2/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8dfbcc4351a0b6d2f2d77f367552f48ffefafe18
- https://github.com/torvalds/linux/commit/8dfbcc4351a0b6d2f2d77f367552f48ffefafe18
