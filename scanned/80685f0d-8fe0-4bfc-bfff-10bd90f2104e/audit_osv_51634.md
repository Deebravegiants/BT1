# [M] CVE-2021-3679

## Summary
Severity: Medium
Advisory: CVE-2021-3679
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/CVE-2021-3679
Type: osv

## Details
A lack of CPU resource in the Linux kernel tracing module functionality in versions prior to 5.14-rc3 was found in the way user uses trace ring buffer in a specific way. Only privileged local users (with CAP_SYS_ADMIN capability) could use this flaw to starve the resources causing denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2021/10/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://www.debian.org/security/2021/dsa-4978
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=67f0d6d9883c13174669f88adac4f0ee656cc16a
- https://bugzilla.redhat.com/show_bug.cgi?id=1989165
