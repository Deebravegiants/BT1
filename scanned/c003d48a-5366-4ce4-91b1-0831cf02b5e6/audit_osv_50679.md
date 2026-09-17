# [M] CVE-2020-27825

## Summary
Severity: Medium
Advisory: CVE-2020-27825
Aliases: A-175769054, PUB-A-175769054
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-27825
Type: osv

## Details
A use-after-free flaw was found in kernel/trace/ring_buffer.c in Linux kernel (before 5.10-rc1). There was a race problem in trace_open and resize of cpu buffer running parallely on different cpus, may cause a denial of service problem (DOS). This flaw could even allow a local attacker with special user privilege to a kernel information leak threat.

## References
- https://lists.debian.org/debian-lts-announce/2021/02/msg00018.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://security.netapp.com/advisory/ntap-20210521-0008/
- https://www.debian.org/security/2021/dsa-4843
- https://bugzilla.redhat.com/show_bug.cgi?id=1905155
