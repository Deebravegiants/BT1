# [H] CVE-2016-7910

## Summary
Severity: High
Advisory: CVE-2016-7910
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2016-7910
Type: osv

## Details
Use-after-free vulnerability in the disk_seqf_stop function in block/genhd.c in the Linux kernel before 4.7.1 allows local users to gain privileges by leveraging the execution of a certain stop operation even if the corresponding start operation had failed.

## References
- https://access.redhat.com/errata/RHSA-2017:1298
- https://access.redhat.com/errata/RHSA-2017:1308
- http://source.android.com/security/bulletin/2016-11-01.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.1
- http://www.securityfocus.com/bid/94135
- https://access.redhat.com/errata/RHSA-2017:0892
- https://access.redhat.com/errata/RHSA-2017:1297
- https://github.com/torvalds/linux/commit/77da160530dd1dc94f6ae15a981f24e5f0021e84
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=77da160530dd1dc94f6ae15a981f24e5f0021e84
