# [M] CVE-2016-7915

## Summary
Severity: Medium
Advisory: CVE-2016-7915
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2016-7915
Type: osv

## Details
The hid_input_field function in drivers/hid/hid-core.c in the Linux kernel before 4.6 allows physically proximate attackers to obtain sensitive information from kernel memory or cause a denial of service (out-of-bounds read) by connecting a device, as demonstrated by a Logitech DJ receiver.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://source.android.com/security/bulletin/2016-11-01.html
- http://www.securityfocus.com/bid/94138
- https://github.com/torvalds/linux/commit/50220dead1650609206efe91f0cc116132d59b3f
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=50220dead1650609206efe91f0cc116132d59b3f
