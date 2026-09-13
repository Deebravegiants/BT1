# [M] af_unix: Fix a data-race in unix_dgram_peer_wake_me().

## Summary
Severity: Medium
Advisory: CVE-2022-49344
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49344
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

af_unix: Fix a data-race in unix_dgram_peer_wake_me().

unix_dgram_poll() calls unix_dgram_peer_wake_me() without `other`'s
lock held and check if its receive queue is full.  Here we need to
use unix_recvq_full_lockless() instead of unix_recvq_full(), otherwise
KCSAN will report a data-race.

## References
- https://git.kernel.org/stable/c/556720013c36c193d9cbfb06e7b33e51f0c39fbf
- https://git.kernel.org/stable/c/662a80946ce13633ae90a55379f1346c10f0c432
- https://git.kernel.org/stable/c/71e8bfc7f838cabc60cba24e09ca84c4f8321ab2
- https://git.kernel.org/stable/c/8801eb3ccd2e4e3b1a01449383e3321ae6dbd9d6
- https://git.kernel.org/stable/c/95f0ba806277733bf6024e23e27e1be773701cca
- https://git.kernel.org/stable/c/c61848500a3fd6867dfa4834b8c7f97133eceb9f
- https://git.kernel.org/stable/c/c926ae58f24f7bd55aa2ea4add9f952032507913
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49344.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49344
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
