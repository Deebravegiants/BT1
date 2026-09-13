# [H] CVE-2023-6931

## Summary
Severity: High
Advisory: CVE-2023-6931
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-19
Source: https://osv.dev/vulnerability/CVE-2023-6931
Type: osv

## Details
A heap out-of-bounds write vulnerability in the Linux kernel's Performance Events system component can be exploited to achieve local privilege escalation.

A perf_event's read_size can overflow, leading to an heap out-of-bounds increment or write in perf_read_group().

We recommend upgrading past commit 382c27f4ed28f803b1f1473ac2d8db0afc795a1b.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=382c27f4ed28f803b1f1473ac2d8db0afc795a1b
- https://kernel.dance/382c27f4ed28f803b1f1473ac2d8db0afc795a1b
