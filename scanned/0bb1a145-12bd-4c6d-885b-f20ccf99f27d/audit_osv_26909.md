# [H] Out-of-bounds write in Linux kernel's Linux Kernel Performance Events (perf) component

## Summary
Severity: High
Advisory: CVE-2023-5717
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-5717
Type: osv

## Details
A heap out-of-bounds write vulnerability in the Linux kernel's Linux Kernel Performance Events (perf) component can be exploited to achieve local privilege escalation.

If perf_read_group() is called while an event's sibling_list is smaller than its child's sibling_list, it can increment or write to memory locations outside of the allocated buffer.

We recommend upgrading past commit 32671e3799ca2e4590773fd0e63aaa4229e50c06.

## References
- https://git.kernel.org
- https://kernel.dance/32671e3799ca2e4590773fd0e63aaa4229e50c06
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5717.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5717
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/kernel/events?id=32671e3799ca2e4590773fd0e63aaa4229e50c06
