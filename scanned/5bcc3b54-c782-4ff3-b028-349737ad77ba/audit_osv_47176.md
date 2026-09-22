# [H] CVE-2016-10088

## Summary
Severity: High
Advisory: CVE-2016-10088
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-30
Source: https://osv.dev/vulnerability/CVE-2016-10088
Type: osv

## Details
The sg implementation in the Linux kernel through 4.9 does not properly restrict write operations in situations where the KERNEL_DS option is set, which allows local users to read or write to arbitrary kernel memory locations or cause a denial of service (use-after-free) by leveraging access to a /dev/sg device, related to block/bsg.c and drivers/scsi/sg.c.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-9576.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0817.html
- http://www.securityfocus.com/bid/95169
- http://www.securitytracker.com/id/1037538
- https://access.redhat.com/errata/RHSA-2017:2077
- http://www.openwall.com/lists/oss-security/2016/12/30/1
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2669
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=128394eff343fc6d2f32172f03e24829539c5835
- https://github.com/torvalds/linux/commit/128394eff343fc6d2f32172f03e24829539c5835
