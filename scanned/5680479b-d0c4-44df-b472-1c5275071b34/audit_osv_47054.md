# [C] CVE-2015-8812

## Summary
Severity: Critical
Advisory: CVE-2015-8812
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2015-8812
Type: osv

## Details
drivers/infiniband/hw/cxgb3/iwch_cm.c in the Linux kernel before 4.5 does not properly identify error conditions, which allows remote attackers to execute arbitrary code or cause a denial of service (use-after-free) via crafted packets.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=67f1aee6f45059fd6b0f5b0ecb2c97ad0451f6b3
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00094.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
