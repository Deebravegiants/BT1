# [H] tcp: fix a signed-integer-overflow bug in tcp_add_backlog()

## Summary
Severity: High
Advisory: CVE-2022-50865
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2022-50865
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.4.278, >=5.5.0 <5.10.153, >=5.11.0 <5.15.77, >=5.16.0 <6.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: fix a signed-integer-overflow bug in tcp_add_backlog()

The type of sk_rcvbuf and sk_sndbuf in struct sock is int, and
in tcp_add_backlog(), the variable limit is caculated by adding
sk_rcvbuf, sk_sndbuf and 64 * 1024, it may exceed the max value
of int and overflow. This patch reduces the limit budget by
halving the sndbuf to solve this issue since ACK packets are much
smaller than the payload.

## References
- https://git.kernel.org/stable/c/28addf029417d53b1df062b4c87feb7bc033cb5f
- https://git.kernel.org/stable/c/4f23cb2be530785db284a685d1b1c30224d8a538
- https://git.kernel.org/stable/c/9d04b4d0feee12bce6bfe37f30d8e953d3c30368
- https://git.kernel.org/stable/c/a85d39f14aa8a71e29cfb5eb5de02878a8779898
- https://git.kernel.org/stable/c/ec791d8149ff60c40ad2074af3b92a39c916a03f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50865.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50865
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
