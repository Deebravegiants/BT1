# [C] RDMA/rxe: Fix seg fault in rxe_comp_queue_pkt

## Summary
Severity: Critical
Advisory: CVE-2024-38544
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38544
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix seg fault in rxe_comp_queue_pkt

In rxe_comp_queue_pkt() an incoming response packet skb is enqueued to the
resp_pkts queue and then a decision is made whether to run the completer
task inline or schedule it. Finally the skb is dereferenced to bump a 'hw'
performance counter. This is wrong because if the completer task is
already running in a separate thread it may have already processed the skb
and freed it which can cause a seg fault.  This has been observed
infrequently in testing at high scale.

This patch fixes this by changing the order of enqueuing the packet until
after the counter is accessed.

## References
- https://git.kernel.org/stable/c/21b4c6d4d89030fd4657a8e7c8110fd941049794
- https://git.kernel.org/stable/c/2b23b6097303ed0ba5f4bc036a1c07b6027af5c6
- https://git.kernel.org/stable/c/30df4bef8b8e183333e9b6e9d4509d552c7da6eb
- https://git.kernel.org/stable/c/bbad88f111a1829f366c189aa48e7e58e57553fc
- https://git.kernel.org/stable/c/c91fb72a2ca6480d8d77262eef52dc5b178463a3
- https://git.kernel.org/stable/c/de5a059e36657442b5637cc16df5163e435b9cb4
- https://git.kernel.org/stable/c/e0e14dd35d4242340c7346aac60c7ff8fbf87ffc
- https://git.kernel.org/stable/c/faa8d0ecf6c9c7c2ace3ca3e552180ada6f75e19
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38544.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38544
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
