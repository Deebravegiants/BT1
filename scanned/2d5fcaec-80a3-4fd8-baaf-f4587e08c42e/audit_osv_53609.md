# [M] CVE-2023-0590

## Summary
Severity: Medium
Advisory: CVE-2023-0590
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-23
Source: https://osv.dev/vulnerability/CVE-2023-0590
Type: osv

## Details
A use-after-free flaw was found in qdisc_graft in net/sched/sch_api.c in the Linux Kernel due to a race problem. This flaw leads to a denial of service issue. If patch ebda44da44f6 ("net: sched: fix race condition in qdisc_graft()") not applied yet, then kernel could be affected.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://lore.kernel.org/all/20221018203258.2793282-1-edumazet%40google.com/
