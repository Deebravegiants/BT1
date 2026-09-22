# [H] ipv6: fix possible UAF in ip6_finish_output2()

## Summary
Severity: High
Advisory: CVE-2024-44986
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44986
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.166, >=5.16.0 <6.1.107, >=6.2.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: fix possible UAF in ip6_finish_output2()

If skb_expand_head() returns NULL, skb has been freed
and associated dst/idev could also have been freed.

We need to hold rcu_read_lock() to make sure the dst and
associated idev are alive.

## References
- https://git.kernel.org/stable/c/3574d28caf9a09756ae87ad1ea096c6f47b6101e
- https://git.kernel.org/stable/c/56efc253196751ece1fc535a5b582be127b0578a
- https://git.kernel.org/stable/c/6ab6bf731354a6fdbaa617d1ec194960db61cf3b
- https://git.kernel.org/stable/c/da273b377ae0d9bd255281ed3c2adb228321687b
- https://git.kernel.org/stable/c/e891b36de161fcd96f12ff83667473e5067b9037
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44986.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44986
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
