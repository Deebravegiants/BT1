# [H] CVE-2015-8955

## Summary
Severity: High
Advisory: CVE-2015-8955
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-10-10
Source: https://osv.dev/vulnerability/CVE-2015-8955
Type: osv

## Details
arch/arm64/kernel/perf_event.c in the Linux kernel before 4.1 on arm64 platforms allows local users to gain privileges or cause a denial of service (invalid pointer dereference) via vectors involving events that are mishandled during a span of multiple HW PMUs.

## References
- http://source.android.com/security/bulletin/2016-10-01.html
- http://www.securityfocus.com/bid/93314
- https://github.com/torvalds/linux/commit/8fff105e13041e49b82f92eef034f363a6b1c071
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8fff105e13041e49b82f92eef034f363a6b1c071
- https://github.com/torvalds/linux/commit/8fff105e13041e49b82f92eef034f363a6b1c071
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8fff105e13041e49b82f92eef034f363a6b1c071
- https://github.com/torvalds/linux/commit/8fff105e13041e49b82f92eef034f363a6b1c071
- http://www.securityfocus.com/bid/93314
