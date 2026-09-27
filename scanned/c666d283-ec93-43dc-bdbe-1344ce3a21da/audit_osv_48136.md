# [H] CVE-2017-18595

## Summary
Severity: High
Advisory: CVE-2017-18595
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2017-18595
Type: osv

## Details
An issue was discovered in the Linux kernel before 4.14.11. A double free may be caused by the function allocate_trace_buffer in the file kernel/trace/trace.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00037.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=4397f04575c44e1440ec2e49b6302785c95fd2f8
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.11
