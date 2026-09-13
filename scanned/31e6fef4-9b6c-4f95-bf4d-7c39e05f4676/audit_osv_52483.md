# [M] CVE-2021-47498

## Summary
Severity: Medium
Advisory: CVE-2021-47498
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47498
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm rq: don't queue request to blk-mq during DM suspend

DM uses blk-mq's quiesce/unquiesce to stop/start device mapper queue.

But blk-mq's unquiesce may come from outside events, such as elevator
switch, updating nr_requests or others, and request may come during
suspend, so simply ask for blk-mq to requeue it.

Fixes one kernel panic issue when running updating nr_requests and
dm-mpath suspend/resume stress test.

## References
- https://git.kernel.org/stable/c/8050652810bf38241edec8717393d2446e8036f1
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://git.kernel.org/stable/c/8ca9745efe3528feb06ca4e117188038eea2d351
- https://git.kernel.org/stable/c/b4459b11e84092658fa195a2587aff3b9637f0e7
