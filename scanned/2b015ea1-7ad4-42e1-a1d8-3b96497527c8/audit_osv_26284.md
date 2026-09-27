# [H] fbdev: Fix invalid page access after closing deferred I/O devices

## Summary
Severity: High
Advisory: CVE-2023-52731
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52731
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: Fix invalid page access after closing deferred I/O devices

When a fbdev with deferred I/O is once opened and closed, the dirty
pages still remain queued in the pageref list, and eventually later
those may be processed in the delayed work.  This may lead to a
corruption of pages, hitting an Oops.

This patch makes sure to cancel the delayed work and clean up the
pageref list at closing the device for addressing the bug.  A part of
the cleanup code is factored out as a new helper function that is
called from the common fb_release().

## References
- https://git.kernel.org/stable/c/3efc61d95259956db25347e2a9562c3e54546e20
- https://git.kernel.org/stable/c/87b9802ca824fcee7915e717e9a60471af62e8e9
- https://git.kernel.org/stable/c/f1d91f0e9d5a240a809698d7d9c5a538e7dcc149
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52731.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52731
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
