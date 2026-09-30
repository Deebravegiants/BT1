# [M] CVE-2016-10723

## Summary
Severity: Medium
Advisory: CVE-2016-10723
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-21
Source: https://osv.dev/vulnerability/CVE-2016-10723
Type: osv

## Details
An issue was discovered in the Linux kernel through 4.17.2. Since the page allocator does not yield CPU resources to the owner of the oom_lock mutex, a local unprivileged user can trivially lock up the system forever by wasting CPU resources from the page allocator (e.g., via concurrent page fault events) when the global OOM killer is invoked. NOTE: the software maintainer has not accepted certain proposed patches, in part because of a viewpoint that "the underlying problem is non-trivial to handle.

## References
- https://www.spinics.net/lists/linux-mm/msg117896.html
- https://patchwork.kernel.org/patch/10395909/
- https://patchwork.kernel.org/patch/9842889/
