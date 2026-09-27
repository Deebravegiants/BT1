# [H] CVE-2017-18202

## Summary
Severity: High
Advisory: CVE-2017-18202
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-27
Source: https://osv.dev/vulnerability/CVE-2017-18202
Type: osv

## Details
The __oom_reap_task_mm function in mm/oom_kill.c in the Linux kernel before 4.14.4 mishandles gather operations, which allows attackers to cause a denial of service (TLB entry leak or use-after-free) or possibly have unspecified other impact by triggering a copy_to_user call within a certain time window.

## References
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.4
- http://www.securityfocus.com/bid/103161
- https://access.redhat.com/errata/RHSA-2018:2772
- https://github.com/torvalds/linux/commit/687cb0884a714ff484d038e9190edc874edcf146
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=687cb0884a714ff484d038e9190edc874edcf146
