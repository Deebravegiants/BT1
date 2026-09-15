# [H] CVE-2015-9004

## Summary
Severity: High
Advisory: CVE-2015-9004
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-05-02
Source: https://osv.dev/vulnerability/CVE-2015-9004
Type: osv

## Details
kernel/events/core.c in the Linux kernel before 3.19 mishandles counter grouping, which allows local users to gain privileges via a crafted application, related to the perf_pmu_register and perf_event_open functions.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c3c87e770458aa004bd7ed3f29945ff436fd6511
- http://www.securityfocus.com/bid/98166
- https://github.com/torvalds/linux/commit/c3c87e770458aa004bd7ed3f29945ff436fd6511
- https://source.android.com/security/bulletin/2017-05-01
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c3c87e770458aa004bd7ed3f29945ff436fd6511
- https://github.com/torvalds/linux/commit/c3c87e770458aa004bd7ed3f29945ff436fd6511
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c3c87e770458aa004bd7ed3f29945ff436fd6511
- https://github.com/torvalds/linux/commit/c3c87e770458aa004bd7ed3f29945ff436fd6511
