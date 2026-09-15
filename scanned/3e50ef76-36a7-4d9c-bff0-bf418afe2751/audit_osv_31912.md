# [H] net: mctp: unshare packets when reassembling

## Summary
Severity: High
Advisory: CVE-2025-21972
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21972
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mctp: unshare packets when reassembling

Ensure that the frag_list used for reassembly isn't shared with other
packets. This avoids incorrect reassembly when packets are cloned, and
prevents a memory leak due to circular references between fragments and
their skb_shared_info.

The upcoming MCTP-over-USB driver uses skb_clone which can trigger the
problem - other MCTP drivers don't share SKBs.

A kunit test is added to reproduce the issue.

## References
- https://git.kernel.org/stable/c/5c47d5bfa7b096cf8890afac32141c578583f8e0
- https://git.kernel.org/stable/c/f44fff3d3c6cd67b6f348b821d73c4d6888c7a6e
- https://git.kernel.org/stable/c/f5d83cf0eeb90fade4d5c4d17d24b8bee9ceeecc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21972.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21972
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
